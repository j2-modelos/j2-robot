import json
from dataclasses import dataclass

@dataclass
class Mensagem:
    acao: str
    tarefa: str

def from_json(json_str):
    try:
        # Converte o JSON em um dicionário
        data = json.loads(json_str)
        # Cria um objeto da dataclass Mensagem a partir do dicionário
        return Mensagem(**data)
    except json.JSONDecodeError:
        print(f"Erro ao parsear JSON: {json_str}")
        return None
