import os

from selenium import webdriver
import time
import json


class EtiquetaServico:
    def __init__(self, driver):
        self._driver = driver

        web_root = os.getenv('PJE_PAYLOAD_WEB_ROOT')
        self.base_url = f"{web_root}/seam/resource/rest/pje-legacy/painelUsuario"

    def execute_fetch(self, endpoint, method='GET', body=None, headers=None):
        url = self.base_url + endpoint  # Concatenando o endpoint com a URL base
        script = f"""
                return (async function() {{
                    try {{
                        let response = await fetch("{url}", {{
                            method: "{method}",
                            headers: {{ "Content-Type": "application/json" }},
                            body: JSON.stringify({json.dumps(body) if body else 'null'}),
                            credentials: "include"
                        }});
                        let data = await response.json();
                        return data;
                    }} catch (err) {{
                        return {{ error: err.message }};
                    }}
                }})();
                """
        return self._driver.execute_script(script)

    def inserir_etiqueta_processo(self, id_processo, etiqueta):
        """
        Método para criar inserir uma etiqueta em um processo.
        """
        return self.execute_fetch("/processoTags/inserir", method='POST', body={
            "idProcesso": str(id_processo),
            "tag": etiqueta
        })

    def inserir_subetiqueta_processo(self, id_processo, subetiqueta: str, etiqueta_pai: str):
        """
        Método para criar uma subetiqueta de um etiqueta existente.
        Caso a etiqueta pai não exista, ocorrerá uma exceção.
        """
        resposta_fetch = self.pesquisar_etiquetas(subetiqueta)
        eventual_subetiqueta_entity = None
        if 'entities' in resposta_fetch:
            nome_completo_subetiqueta_a_inserir = f"{etiqueta_pai} > {subetiqueta}"
            eventual_subetiqueta_entity = next(
                (e for e in resposta_fetch['entities'] if e['nomeTagCompleto'] == nome_completo_subetiqueta_a_inserir), None)

        if not eventual_subetiqueta_entity is None:
            return self.inserir_etiqueta_processo(id_processo, eventual_subetiqueta_entity["nomeTagCompleto"])
        else:
            resposta_fetch = self.pesquisar_etiquetas(etiqueta_pai)
            etiqueta_pai_entity = next((e for e in resposta_fetch['entities'] if e['nomeTagCompleto'] == etiqueta_pai), None)
            if etiqueta_pai_entity is None:
                raise Exception("A etiqueta pai precisa existir antes de criar a subetiqueta")

            nova_etiqueta_entity = self.execute_fetch("/tags", method='POST', body={
                "id": None,
                "idPai": int(etiqueta_pai_entity["id"]),
                "marcado": False,
                "nomeTag": subetiqueta,
                "nomeTagCompleto": f"{etiqueta_pai_entity["nomeTagCompleto"]} > {subetiqueta}",
                "pai": {
                    "id": int(etiqueta_pai_entity["id"])
                },
                "possuiFilhos": False
            })

            return self.inserir_etiqueta_processo(id_processo, nova_etiqueta_entity["nomeTagCompleto"])


    def remover_etiqueta_processo(self, id_processo, id_etiqueta):
        """
        Método para criar inserir uma etiqueta em um processo.
        """
        return self.execute_fetch("/processoTags/remover", method='POST', body={
            "id_processo": int(id_processo),
            "idTag": int(id_etiqueta)
        })

    def pesquisar_etiquetas(self, texto_etiqueta: str):
        """
        Método para pesquisar etiquetas pelo texto.
        """
        return self.execute_fetch("/etiquetas", method='POST', body={
            "tagsString": str(texto_etiqueta)
        })