import re
import unicodedata


def transformar_em_nome_classe(s):
    # Normaliza a string para remover acentos
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')

    # Remove caracteres não alfanuméricos
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s)

    # Converte os espaços para a primeira letra maiúscula de cada palavra
    s = ''.join(word.capitalize() for word in s.split())

    return s


def criar_acronimo(texto):
    # Lista de preposições e conjunções a serem ignoradas
    palavras_ignoradas = [
        "a", "ante", "até", "com", "contra", "de", "desde", "em", "entre",
        "para", "perante", "por", "sem", "sob", "sobre", "tras",  # Preposições
        "e", "nem", "mas", "porém", "contudo", "todavia", "logo", "portanto",
        "assim", "porque", "que", "pois", "ou", "caso", "se", "como", "quando",
        "enquanto", "antes que", "seque", "conforme", "segundo", "a fim de que",  # Conjunções
    ]

    # Dividir a string em palavras
    palavras = texto.lower().split()
    # Filtrar palavras e pegar a primeira letra de cada uma (ignorando as preposições)
    acronimo = ''.join([palavra[0].upper() for palavra in palavras if palavra not in palavras_ignoradas])

    return acronimo

