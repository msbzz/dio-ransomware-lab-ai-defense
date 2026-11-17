# -*- coding: utf-8 -*-
"""Recuperação didática: verifica e restaura cópias criptografadas."""
from pathlib import Path
import sys
from cryptography.fernet import Fernet, InvalidToken

NOMES = ('clientes.txt', 'confidencial.txt', 'contrato.txt', 'financeiro.txt', 'interno.txt')


def localizar():
    pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
    if pasta.name.lower() != 'simulador':
        raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
    if pasta.parent.name.lower() == 'ransomwarelab':
        return pasta.parent, 'laboratorio'
    if pasta.parent.name.lower() == 'lab-ransomware':
        return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
    raise RuntimeError('Caminho não reconhecido.')


def main():
    lab, modo = localizar()
    amostras = lab / 'amostras'
    chave = lab / 'simulador' / 'chave_recuperacao.key'
    if chave.is_symlink() or not chave.is_file() or not amostras.is_dir():
        raise RuntimeError('Chave ou pasta de amostras ausente.')
    cifrador = Fernet(chave.read_bytes())
    resultados = []
    for nome in NOMES:
        origem = amostras / (nome + '.encrypted')
        if origem.is_symlink() or not origem.is_file():
            raise RuntimeError('Arquivo criptografado ausente: ' + nome)
        try:
            dados = cifrador.decrypt(origem.read_bytes())
        except InvalidToken:
            raise RuntimeError('Chave inválida ou arquivo danificado: ' + nome)
        resultados.append((nome, dados))
    print('Modo detectado:', modo)
    print('Cinco arquivos validados. Os originais existentes não serão sobrescritos.')
    if input('Digite RECUPERAR para continuar: ') != 'RECUPERAR':
        print('Cancelado.')
        return
    # Se o original já existir, só verificamos seu conteúdo.
    # Se não existir, restauramos uma nova cópia, sem apagar o .encrypted.
    for nome, dados in resultados:
        destino = amostras / nome
        if destino.is_symlink():
            raise RuntimeError('Destino inválido: ' + nome)
        if destino.exists():
            if destino.read_bytes() != dados:
                raise RuntimeError('Original diferente; não sobrescrever: ' + nome)
            print('[CONFERIDO]', nome)
        else:
            with destino.open('xb') as f:
                f.write(dados)
            print('[RECUPERADO]', nome)
    print('Concluído. Arquivos .encrypted, backups e chave preservados.')


if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
