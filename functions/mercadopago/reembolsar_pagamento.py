import requests
import os

def reembolsar_pagamento(paymentID):
    acesstoken = os.getenv("MERCADOPAGO_TOKEN")

    url = f"https://api.mercadopago.com/v1/payments/{paymentID}/refunds"
    headers = {
        "Authorization": f"Bearer {acesstoken}"
    }
    requests.post(url=url, headers=headers)
    return