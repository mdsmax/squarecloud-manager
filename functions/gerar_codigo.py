import random
import string

def gerar_codigo(tamanho=10):
    caracteres = string.ascii_letters + string.digits
    codigo = ''.join(random.choice(caracteres) for _ in range(tamanho))
    return codigo