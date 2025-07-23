import json

class Database:
    @staticmethod
    def obter(filename: str):
        with open(f"database/{filename}", "r") as file:
            return json.load(file)
    
    @staticmethod
    def salvar(filename: str, data: dict):
        with open(f"database/{filename}", "w") as file:
            json.dump(data, file, indent=4)