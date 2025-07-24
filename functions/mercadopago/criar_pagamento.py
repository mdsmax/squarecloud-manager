import mercadopago
import os
from .criar_qr_code import criar_qr_code

def criar_pagamento(valor: float):
    sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_TOKEN"))
    payment_data = {
        "transaction_amount": valor,
        "payment_method_id": "pix",
        "payer": {
            "email": "eu@mdsmax.dev"
        }
    }

    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]

    if "point_of_interaction" in payment:
        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code"]
        payment = payment["id"]
    else:
        return False

    qrcodeURL = criar_qr_code(qr_code)

    return qr_code, qrcodeURL, payment