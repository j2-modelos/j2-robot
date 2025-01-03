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
        "a", "ante", "até", "com", "contra", "de", "da", "do", "das", "dos", "desde", "em", "entre",
        "para", "perante", "por", "sem", "sob", "sobre", "tras",  # Preposições
        "e", "nem", "mas", "no", "na", "nos", "nas", "porém", "contudo", "todavia", "logo", "portanto",
        "assim", "porque", "que", "pois", "ou", "caso", "se", "como", "quando",
        "enquanto", "antes que", "seque", "conforme", "segundo", "a fim de que",  # Conjunções
    ]

    # Substituir caracteres especiais por espaços em branco
    texto_limpo = re.sub(r'[^\w\s]', ' ', texto)

    # Dividir a string em palavras
    palavras = texto_limpo.split()

    # Construir acrônimo considerando palavras ignoradas e palavras em maiúsculas
    acronimo = ''.join([
        palavra if palavra.isupper() else palavra[0].upper()
        for palavra in palavras
        if palavra.lower() not in palavras_ignoradas
    ])

    return acronimo

# Função que recebe uma string e retorna a UUID encontrada
def extract_uuid(string):
    # Expressão regular para encontrar uma UUID no formato padrão
    uuid_pattern = r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b'
    match = re.search(uuid_pattern, string)  # Usa re.search para procurar a UUID
    return match.group(0) if match else None  # Retorna a UUID encontrada ou None


# Se o script for executado diretamente, esta parte será executada
if __name__ == "__main__":
    # Exemplo de uso
    example_string = "Aqui está sua UUID: 123e4567-e89b-12d3-a456-426614174000 em algum lugar."
    uuid = extract_uuid(example_string)

    # Exibindo o resultado
    if uuid:
        print(f"UUID encontrada: {uuid}")
    else:
        print("Nenhuma UUID válida foi encontrada.")


    for name in ["Avaliar determinações do magistrado",
                 "Preparar intimação", "Preparar citação e/ou intimação",
                 "Instituto Nacional de Ciência e Tecnologia - Amazônia Sustentável",
                 "Publicar DJE",
                 "Certificar consulta INFOJUD"]:
        print(f"{name} -> {criar_acronimo(name)}")

