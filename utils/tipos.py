def normalizar_valor_boolean(valor):
    """
    Normaliza o valor para o tipo booleano (True ou False).

    Parâmetros:
        valor (str, bool): O valor a ser normalizado. Pode ser uma string representando um valor
                           booleano (como 'true', 'sim', '1', 'false', 'nao', 'não', '0') ou um valor
                           booleano (True ou False).

    Retorna:
        bool ou None: Retorna True ou False, conforme o valor fornecido. Se o valor não puder ser
                      interpretado como booleano, retorna None.

    Exemplos:
        normalizar_valor_boolean('sim')   # Retorna True
        normalizar_valor_boolean('não')   # Retorna False
        normalizar_valor_boolean(True)    # Retorna True
        normalizar_valor_boolean('0')     # Retorna False
        normalizar_valor_boolean('foo')   # Retorna None
    """
    if isinstance(valor, str):
        valor = valor.strip().lower()
        if valor in ['true', 'sim', '1']:
            return True
        elif valor in ['false', 'nao', 'não', '0']:
            return False
    elif isinstance(valor, bool):
        return valor
    return None
