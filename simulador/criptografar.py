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
    if chave.exists() or chave.is_symlink():
        raise RuntimeError('Já existe uma chave. Recupere o teste anterior primeiro.')

    # Verifica todos os arquivos antes de iniciar a operação.
    pares = []
    for nome in NOMES:
        origem = pasta / nome
        destino = pasta / (nome + '.encrypted')
        validar_arquivo(origem)
        if destino.exists() or destino.is_symlink():
            raise RuntimeError('Arquivo criptografado já existe: ' + destino.name)
        pares.append((origem, destino))

    print('Laboratório:', lab)
    print('Os cinco arquivos .txt serão convertidos em .encrypted na pasta amostras.')
    if input('Digite SIMULAR para confirmar: ') != 'SIMULAR':
        print('Cancelado.')
        return

    # Lê e criptografa os cinco documentos antes de modificar a pasta.
    token = Fernet.generate_key()
    fernet = Fernet(token)
    dados = [(origem, destino, fernet.encrypt(origem.read_bytes())) for origem, destino in pares]
    # A chave é salva separadamente, para permitir a recuperação.
    with chave.open('xb') as arquivo:
        arquivo.write(token)

    # Cada arquivo criptografado é conferido antes de retirar o .txt correspondente.
    for origem, destino, conteudo in dados:
        with destino.open('xb') as arquivo:
            arquivo.write(conteudo)
        if fernet.decrypt(destino.read_bytes()) != origem.read_bytes():
            raise RuntimeError('Falha na validação: ' + origem.name)
        origem.unlink()
        print('[CRIPTOGRAFADO]', destino.name)
    print('Concluído. A chave está na pasta simulador.')


if __name__ == '__main__':
    try:
        main()
    except Exception as erro:
        print('[ERRO]', erro)
        sys.exit(1)
