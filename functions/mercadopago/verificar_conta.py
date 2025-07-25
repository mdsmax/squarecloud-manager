import requests
import os

def verificar_conta() -> bool:
    headers = {
        "Authorization": f"Bearer {os.getenv('MERCADOPAGO_TOKEN')}"
    }
    verificar = requests.get(url="https://api.mercadopago.com/users/me", headers=headers)
    if verificar.status_code == 200:
        return True
    else:
        return False