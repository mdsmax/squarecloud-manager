import os
import shutil
import asyncio

def limpar_temp(temp_dir=".temp"):
    for name in os.listdir(temp_dir):
        path = os.path.join(temp_dir, name)
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            print(f"Erro ao remover {path}: {e}")

async def limpar_temp_task():
    while True:
        limpar_temp()
        await asyncio.sleep(600)