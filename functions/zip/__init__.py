from .descompactar import descompactar
from .list import listar_arquivos
from .verify_squarecloud_config import verify_squarecloud, formatar_config
from .compactar_conteudo import zipar_conteudo

class Zip:
    descompactar = descompactar
    listar_arquivos = listar_arquivos
    verify_squarecloud = verify_squarecloud
    formatar_config = formatar_config
    zipar_conteudo = zipar_conteudo