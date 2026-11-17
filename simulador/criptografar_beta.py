# -*- coding: utf-8 -*-
"""Laboratório didático: criptografa cópias de cinco amostras, preservando originais."""
from pathlib import Path
import sys
import shutil
import hashlib
from cryptography.fernet import Fernet

NOMES = ('clientes.txt', 'confidencial.txt', 'contrato.txt', 'financeiro.txt', 'interno.txt')


def localizar():
    # No executável, sys.executable indica onde o .exe está instalado.
    # No Python, __file__ indica onde o próprio .py está salvo.
    pasta = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
    if pasta.name.lower() != 'simulador':
        raise RuntimeError('Execute a partir de uma pasta chamada simulador.')
    if pasta.parent.name.lower() == 'ransomwarelab':
        return pasta.parent, 'laboratorio'
    if pasta.parent.name.lower() == 'lab-ransomware':
        return pasta.parent / 'testes' / 'RansomwareLab', 'desenvolvimento'
    raise RuntimeError('Caminho não reconhecido; operação cancelada.')


def main():
    lab, modo = localizar()
    amostras, backup = lab / 'amostras', lab / 'backup'
    simulador = lab / 'simulador'
    if not amostras.is_dir() or not backup.is_dir() or not simulador.is_dir():
        raise RuntimeError('Estrutura do laboratório incompleta.')
    arquivos = [amostras / nome for nome in NOMES]
    saidas = [amostras / (nome + '.encrypted') for nome in NOMES]
    chave = simulador / 'chave_recuperacao.key'
    # Validação prévia evita sobrescrever resultados de outro teste.
    for arq, saida in zip(arquivos, saidas):
        if arq.is_symlink() or not arq.is_file() or saida.exists() or saida.is_symlink():
            raise RuntimeError('Amostra ausente ou resultado existente: ' + arq.name)
    if chave.exists() or chave.is_symlink():
        raise RuntimeError('Já existe chave de recuperação. Preserve a chave anterior.')
    print('Modo detectado:', modo)
    print('Serão criadas cópias criptografadas; originais serão preservados.')
    if input('Digite SIMULAR para continuar: ') != 'SIMULAR':
        print('Cancelado.')
        return
    # Guardamos uma cópia de segurança sem substituir backups existentes.
    for arq in arquivos:
        destino = backup / arq.name
        if destino.is_symlink():
            raise RuntimeError('Backup inválido: ' + destino.name)
        if not destino.exists():
            shutil.copy2(str(arq), str(destino))
    token = Fernet.generate_key()
    with chave.open('xb') as f:
        f.write(token)
    cifrador = Fernet(token)
    for arq, saida in zip(arquivos, saidas):
        with saida.open('xb') as f:
            f.write(cifrador.encrypt(arq.read_bytes()))
        print('[CRIPTOGRAFADO EM CÓPIA]', arq.name)
    print('Concluído. Originais e backups preservados.')


if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
