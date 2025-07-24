import os
import json
import requests

def criar_qr_code(response):
    corMain = "#000000"
    corSec = "#000000"

    payload = {
        "data": str(response),
        "config": {
            "body": "square",
            "eye": "frame0",
            "eyeBall": "ball0",
            "bodyColor": "#000000",
            "bgColor": "#FFFFFF",
            "eye1Color": "#000000",
            "eye2Color": "#000000",
            "eye3Color": "#000000",
            "eyeBall1Color": "#000000",
            "eyeBall2Color": "#000000",
            "eyeBall3Color": "#000000",
            "gradientColor1": f"#{corMain}",
            "gradientColor2": f"#{corSec}",
            "gradientType": "linear",
            "gradientOnEyes": "true",
            "logo": None,
            "logoMode": "default"
        },
        "size": 550,
        "download": "imageUrl",
        "file": "png"
    }

    qrCode = requests.post(url="https://api.qrcode-monkey.com/qr/custom", json=payload)

    if qrCode.status_code == 200:
        return f"https:{qrCode.json()['imageUrl']}"
    else:
        return None