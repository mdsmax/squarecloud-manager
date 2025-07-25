import os
from .list import listar_arquivos

REQUIRED_KEYS = ["MAIN", "MEMORY", "VERSION", "DISPLAY_NAME"]

def verify_squarecloud(pasta: str):
    arquivos = listar_arquivos(pasta)
    for arquivo in arquivos:
        nome = os.path.basename(arquivo)
        if nome in ("squarecloud.config", "squarecloud.app"):
            config = formatar_config(arquivo)
            if config:
                return True
            
    return False


def formatar_config(caminho_arquivo: str):
    config = {}
    if not os.path.isfile(caminho_arquivo):
        return None

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            config[chave.strip()] = valor.strip()

    for key in REQUIRED_KEYS:
        if key not in config:
            return None

    f.close()
    return config