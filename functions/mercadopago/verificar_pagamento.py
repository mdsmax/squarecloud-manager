import mercadopago
import os

from database import Database

def verificar_pagamento(carrinhoID: str):
    sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_TOKEN"))
    carrinho = Database.obter("carrinhos.json")[carrinhoID]
    paymentID = carrinho["payment"]["paymentID"]
    if not paymentID:
        return False
    
    payment_info_response = sdk.payment().get(paymentID)
    payment_info = payment_info_response["response"]

    if payment_info["status"] == "approved":
        return True
    else:
        return False