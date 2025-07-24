import os

def listar_arquivos(pasta: str):
    arquivos = []
    for root, dirs, files in os.walk(pasta):
        for file in files:
            arquivos.append(os.path.join(root, file))
            
    return arquivos