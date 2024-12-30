class DriverGuia:
    """
        Representa uma janela ou guia no aplicação

        Atributos:
            alias (str): Alias para esta guia.
            id (str): O identificador único para selenium desta guia ou janela
        """
    def __init__(self, alias: str, id_: str):
        self.alias = alias
        self.id = id_