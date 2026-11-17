"""DIO Ransomware Lab: simulação controlada, somente em arquivos fictícios."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from cryptography.fernet import Fernet, InvalidToken

ARQUIVOS = ("clientes.txt", "confidencial.txt", "contrato.txt", "financeiro.txt", "interno.txt")


def laboratorio():
    if sys.platform != "win32":
        raise RuntimeError("Laboratório destinado ao Windows.")
    if getattr(sys, "frozen", False):
        return Path(r"C:\RansomwareLab")
    return Path(__file__).resolve().parent.parent / "testes" / "RansomwareLab"


def arquivo_regular(caminho):
    return caminho.is_file() and not caminho.is_symlink()


def hash_arquivo(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def registrar(base, evento, **detalhes):
    evidencias = base / "evidencias"
    if evidencias.is_symlink():
        raise RuntimeError("Pasta de evidências não pode ser um link.")
    evidencias.mkdir(exist_ok=True)
    registro = {"horario_utc": datetime.now(timezone.utc).isoformat(), "evento": evento, **detalhes}
    with (evidencias / "operacoes.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def referencias(base):
    referencia = base / "evidencias" / "hashes_originais.txt"
    if not arquivo_regular(referencia):
        raise RuntimeError("Referência original ausente ou inválida: hashes_originais.txt")
    dados = {}
    for linha in referencia.read_text(encoding="utf-8-sig").splitlines():
        nome, separador, valor = linha.partition(":")
        if not separador or nome.strip() in dados:
            raise RuntimeError("Formato inválido no arquivo de hashes originais")
        dados[nome.strip()] = valor.strip().lower()
    if set(dados) != set(ARQUIVOS) or any(len(v) != 64 or any(c not in '0123456789abcdef' for c in v) for v in dados.values()):
        raise RuntimeError("Hashes originais incompletos ou inválidos")
    return dados


def verificar(base):
    print("=== Verificação do laboratório ===")
    if not base.is_dir() or base.is_symlink():
        raise RuntimeError("Pasta do laboratório ausente ou é um link")
    esperado = referencias(base)
    for pasta_nome in ("amostras", "backup"):
        pasta = base / pasta_nome
        if not pasta.is_dir() or pasta.is_symlink():
            raise RuntimeError(f"Pasta inválida: {pasta}")
        for nome in ARQUIVOS:
            arquivo = pasta / nome
            if not arquivo_regular(arquivo):
                raise RuntimeError(f"Arquivo ausente ou inválido: {arquivo}")
            if hash_arquivo(arquivo) != esperado[nome]:
                raise RuntimeError(f"Hash diferente da referência: {arquivo}")
            print(f"[OK] {pasta_nome}/{nome}")
    print("[OK] Dez verificações de integridade concluídas.")


def pasta_nova(base, nome):
    pasta = base / nome
    if pasta.exists() or pasta.is_symlink():
        raise RuntimeError(f"Destino já existe; nada foi sobrescrito: {pasta}")
    pasta.mkdir()
    return pasta


def simular(base):
    verificar(base)
    resposta = input("Digite SIMULAR para gerar cópias criptografadas dos cinco arquivos: ")
    if resposta != "SIMULAR":
        print("Operação cancelada.")
        return
    chave_destino = base / "evidencias" / "chave_recuperacao.key"
    if chave_destino.exists() or chave_destino.is_symlink():
        raise RuntimeError("Já existe uma chave de recuperação. Operação cancelada.")
    destino = pasta_nova(base, "simulacao")
    chave = Fernet.generate_key()
    # Criação exclusiva, sem sobrescrever chave anterior.
    with chave_destino.open("xb") as f:
        f.write(chave)
    cifra = Fernet(chave)
    for nome in ARQUIVOS:
        origem = base / "amostras" / nome
        saida = destino / (nome + ".encrypted")
        with saida.open("xb") as f:
            f.write(cifra.encrypt(origem.read_bytes()))
        registrar(base, "simulacao_criptografia", arquivo=nome, destino=str(saida), sha256=hash_arquivo(saida))
        print(f"[SIMULADO] {nome}")
    print("\nSIMULAÇÃO EDUCACIONAL: arquivos de teste criptografados em cópias.")
    print("Nenhum arquivo original foi bloqueado ou apagado. Chave salva em evidencias/chave_recuperacao.key")


def recuperar(base):
    chave = base / "evidencias" / "chave_recuperacao.key"
    if not arquivo_regular(chave):
        raise RuntimeError("Chave de recuperação ausente")
    origem = base / "simulacao"
    if not origem.is_dir() or origem.is_symlink():
        raise RuntimeError("Pasta de simulação ausente ou inválida")
    cifra = Fernet(chave.read_bytes())
    # Validar todos antes de criar arquivos de saída.
    conteudo = {}
    for nome in ARQUIVOS:
        arquivo = origem / (nome + ".encrypted")
        if not arquivo_regular(arquivo):
            raise RuntimeError(f"Arquivo criptografado ausente: {nome}")
        try:
            conteudo[nome] = cifra.decrypt(arquivo.read_bytes())
        except InvalidToken as e:
            raise RuntimeError(f"Chave inválida ou arquivo alterado: {nome}") from e
    destino = pasta_nova(base, "recuperados")
    for nome, dados in conteudo.items():
        saida = destino / nome
        with saida.open("xb") as f:
            f.write(dados)
        registrar(base, "recuperacao", arquivo=nome, sha256=hash_arquivo(saida))
        print(f"[RECUPERADO] {nome}")


def validar(base):
    esperado = referencias(base)
    pasta = base / "recuperados"
    if not pasta.is_dir() or pasta.is_symlink():
        raise RuntimeError("Pasta de recuperados ausente ou inválida")
    erros = 0
    for nome in ARQUIVOS:
        arquivo = pasta / nome
        ok = arquivo_regular(arquivo) and hash_arquivo(arquivo) == esperado[nome]
        print(f"[{'OK' if ok else 'ERRO'}] {nome}")
        erros += not ok
    registrar(base, "validacao", resultado="OK" if not erros else "FALHA", divergencias=erros)
    if erros:
        raise RuntimeError(f"{erros} arquivo(s) divergente(s)")
    print("Todos os arquivos recuperados correspondem aos hashes originais.")


def main():
    parser = argparse.ArgumentParser(description="Simulação educacional restrita ao RansomwareLab")
    parser.add_argument("etapa", choices=("verificar", "simular", "recuperar", "validar"))
    args = parser.parse_args()
    base = laboratorio()
    try:
        {"verificar": verificar, "simular": simular, "recuperar": recuperar, "validar": validar}[args.etapa](base)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[ERRO] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
