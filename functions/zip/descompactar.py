import zipfile

def descompactar(arquivo: str, destino: str):
    with zipfile.ZipFile(arquivo, "r") as zip_ref:
        zip_ref.extractall(destino)

    return destino