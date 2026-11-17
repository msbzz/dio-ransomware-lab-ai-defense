
from pathlib import Path
import sys
import hashlib
import shutil

if sys.platform != "win32":
    raise RuntimeError("Este laboratório requer Windows.")

# Pasta do laboratório: executável no Windows 7; código-fonte no Host.

if getattr(sys, "frozen", False):
    LAB_DIR = Path(r"C:\RansomwareLab")
else:
    LAB_DIR = Path(__file__).resolve().parent.parent / "testes" / "RansomwareLab"

# Arquivos fictícios autorizados para a simulação
ARQUIVOS = [
    "clientes.txt",
    "confidencial.txt",
    "contrato.txt",
    "financeiro.txt",
    "interno.txt",
]

def verificar_ambiente():
    print("=== DIO Ransomware Lab ===")

    pasta_amostras = LAB_DIR / "amostras"

    if not pasta_amostras.is_dir():
        print(f"Laboratório não encontrado: {pasta_amostras}")
        return False

    for nome in ARQUIVOS:
        arquivo = pasta_amostras / nome
        if arquivo.is_file() and not arquivo.is_symlink():
            print(f"[OK] {nome}")
        else:
            print(f"[ERRO] {nome} não encontrado")
            return False

    print("Ambiente validado.")
    return True

def calcular_hashes():
    print("\n=== Hashes SHA-256 ===")

    pasta_evidencias = LAB_DIR / "evidencias"
    pasta_evidencias.mkdir(exist_ok=True)

    destino = pasta_evidencias / "hashes_originais.txt"

    if destino.exists() or destino.is_symlink():
        print("[INFO] Hashes originais já registrados. Evidência preservada.")
        return

    # Modo exclusivo: nunca sobrescreve uma evidência existente.
    with destino.open("x", encoding="utf-8") as saida:
        for nome in ARQUIVOS:
            arquivo = LAB_DIR / "amostras" / nome

            if not arquivo.is_file() or arquivo.is_symlink():
                print(f"[ERRO] Arquivo inválido: {nome}")
                continue

            hash_sha256 = hashlib.sha256(arquivo.read_bytes()).hexdigest()

            print(f"{nome}: {hash_sha256}")
            saida.write(f"{nome}: {hash_sha256}\n")

    print(f"\nEvidências salvas em: {destino}")

def verificar_backup():
    print("\n=== Verificação do backup ===")

    for nome in ARQUIVOS:
        original = LAB_DIR / "amostras" / nome
        backup = LAB_DIR / "backup" / nome

        if not original.is_file() or not backup.is_file():
            print(f"[ERRO] Arquivo ausente: {nome}")
            return False

        if original.is_symlink() or backup.is_symlink():
            print(f"[ERRO] Link simbólico não permitido: {nome}")
            return False

        hash_original = hashlib.sha256(original.read_bytes()).hexdigest()
        hash_backup = hashlib.sha256(backup.read_bytes()).hexdigest()

        if hash_original != hash_backup:
            print(f"[ERRO] Hash diferente: {nome}")
            return False

        print(f"[OK] {nome} - Backup íntegro")

    print("Todos os backups foram validados.")
    return True


def criar_backup():
    print("\n=== Backup dos arquivos ===")

    origem = LAB_DIR / "amostras"
    destino = LAB_DIR / "backup"

    destino.mkdir(exist_ok=True)

    for nome in ARQUIVOS:
        arquivo = origem / nome
        copia = destino / nome

        if not arquivo.is_file() or arquivo.is_symlink():
            print(f"[ERRO] Arquivo inválido: {nome}")
            return False

        if copia.exists() or copia.is_symlink():
            print(f"[ERRO] Backup já existe: {nome}")
            return False

        shutil.copy2(arquivo, copia)
        print(f"[BACKUP] {nome}")

    print("Backup concluído.")
    return True



if __name__ == "__main__":
    if verificar_ambiente():
        calcular_hashes()
        verificar_backup()
    
