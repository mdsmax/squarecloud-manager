import os
import zipfile
import shutil

def zipar_conteudo(pasta_origem, zip_destino):
    itens = [f for f in os.listdir(pasta_origem) if not f.startswith('.')]
    if len(itens) == 1 and os.path.isdir(os.path.join(pasta_origem, itens[0])):
        nova_raiz = os.path.join(pasta_origem, itens[0])
    else:
        nova_raiz = pasta_origem

    if not tem_config_na_raiz(nova_raiz):
        mover_config_para_raiz(nova_raiz)

    with zipfile.ZipFile(zip_destino, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(nova_raiz):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=nova_raiz)
                zipf.write(file_path, arcname)

def tem_config_na_raiz(pasta):
    return any(
        os.path.isfile(os.path.join(pasta, f))
        and f in ("squarecloud.config", "squarecloud.app")
        for f in os.listdir(pasta)
    )

def mover_config_para_raiz(pasta):
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file in ("squarecloud.config", "squarecloud.app"):
                src = os.path.join(root, file)
                dst = os.path.join(pasta, file)
                if src != dst:
                    shutil.move(src, dst) 