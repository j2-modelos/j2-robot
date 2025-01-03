import os

import json

from selenium.webdriver.chrome.webdriver import WebDriver


class ProcessoServico:
    def __init__(self, driver):
        self._driver: WebDriver = driver

        web_root = os.getenv('PJE_PAYLOAD_WEB_ROOT')
        self.base_url = f"{web_root}/seam/resource/rest/pje-legacy/processos"

    def execute_fetch(self, endpoint, method='GET', body=None, headers=None):
        url = self.base_url + endpoint  # Concatenando o endpoint com a URL base
        script = f"""
                return (async function() {{
                    try {{
                        let response = await fetch("{url}", {{
                            method: "{method}",
                            headers: {{ "Content-Type": "application/json" }},
                            { f"body: JSON.stringify({json.dumps(body) if body else 'null'})," if body else "" }
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

    def obter_dados_basicos(self, id_processo):
        """
        Método_ para obter dados básicos do processo em um Dict
        """
        return self.execute_fetch(endpoint=f"/{id_processo}", method='GET')