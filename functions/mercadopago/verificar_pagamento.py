import mercadopago
import os

from database import Database

def verificar_pagamento(carrinhoID: str):
    sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_TOKEN"))
    tempo_maximo = 10 * 60
    intervalo = 5
    tempo_decorrido = 0
    carrinho = Database.obter("carrinhos.json")[carrinhoID]
    paymentID = carrinho["payment"]["paymentID"]
    if not paymentID:
        return "Cancelled"

    while tempo_decorrido < tempo_maximo:
            payment_info_response = sdk.payment().get(paymentID)
            payment_info = payment_info_response["response"]

            if payment_info["status"] == "approved":
                return True
            else:
                tempo_decorrido += intervalo
                return False


    return "Cancelled"