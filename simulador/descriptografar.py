# -*- coding: utf-8 -*-
"""Simulação didática limitada a cinco arquivos fictícios do RansomwareLab."""
from pathlib import Path
import sys
from cryptography.fernet import Fernet, InvalidToken

# Lista fechada: nenhum arquivo fora desses nomes é processado.
NOMES = ('clientes.txt', 'confidencial.txt', 'contrato.txt', 'financeiro.txt', 'interno.txt')


def localizar_lab():
    # Executável: a pasta simulador está dentro de RansomwareLab.
    # Código Python: o laboratório de testes fica na pasta testes.
    if getattr(sys, 'frozen', False):
        pasta = Path(sys.executable).resolve().parent
        if pasta.name.lower() != 'simulador':
            raise RuntimeError('O executável deve estar na pasta simulador.')
        lab = pasta.parent
    else:
        lab = Path(__file__).resolve().parent.parent / 'testes' / 'ransomwarelab'
    if lab.name.lower() != 'ransomwarelab':
        raise RuntimeError('Laboratório não encontrado.')
    if not (lab / 'amostras').is_dir() or not (lab / 'simulador').is_dir():
        raise RuntimeError('Estrutura do laboratório incompleta.')
    return lab


def validar_arquivo(caminho):
    # Rejeita atalhos e links simbólicos para não sair do laboratório.
    if caminho.is_symlink() or not caminho.is_file():
        raise RuntimeError('Arquivo ausente ou inválido: ' + caminho.name)

def main():
    if sys.platform != 'win32':
        raise RuntimeError('Execução permitida somente no Windows.')
    lab = localizar_lab()
    pasta = lab / 'amostras'
    chave = lab / 'simulador' / 'chave_recuperacao.key'
    validar_arquivo(chave)
    fernet = Fernet(chave.read_bytes())

    # Valida a recuperação completa em memória, antes de gravar qualquer arquivo.
    pares = []
    for nome in NOMES:
        origem = pasta / (nome + '.encrypted')
        destino = pasta / nome
        validar_arquivo(origem)
        if destino.exists() or destino.is_symlink():
            raise RuntimeError('O arquivo original já existe: ' + nome)
        try:
            conteudo = fernet.decrypt(origem.read_bytes())
        except InvalidToken as erro:
            raise RuntimeError('Chave incorreta ou arquivo danificado: ' + nome) from erro
        pares.append((origem, destino, conteudo))

    print('Cinco arquivos validados para recuperação.')
    if input('Digite RECUPERAR para confirmar: ') != 'RECUPERAR':
        print('Cancelado.')
        return

    # Recria cada .txt e confere o conteúdo antes de retirar o .encrypted.
    for origem, destino, conteudo in pares:
        with destino.open('xb') as arquivo:
            arquivo.write(conteudo)
        if destino.read_bytes() != conteudo:
            raise RuntimeError('Falha na validação: ' + destino.name)
        origem.unlink()
        print('[RECUPERADO]', destino.name)
    print('Concluído. Chave preservada em simulador para auditoria.')


if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
