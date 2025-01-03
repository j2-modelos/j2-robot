import json

from selenium import webdriver
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Dom:
    def __init__(self, driver: webdriver.Chrome):
        """
        Inicializa a classe Dom com a instância do WebDriver.
        :param driver: Instância do WebDriver.
        """
        self.driver = driver

    def insert_html(self, css_selector, position, html_string):
        """
        Insere uma string HTML na posição especificada em relação a um elemento
        encontrado usando document.querySelector.
        :param css_selector: O seletor CSS para localizar o elemento usando querySelector.
        :param position: A posição onde o HTML será inserido, valores possíveis:
            - 'beforebegin': Antes do elemento.
            - 'afterbegin': Como o primeiro filho do elemento.
            - 'beforeend': Como o último filho do elemento.
            - 'afterend': Após o elemento.
        :param html_string: A string de HTML a ser inserida.
        """
        try:
            # Script utilizando document.querySelector no lado do JavaScript
            script = """
            var element = document.querySelector(arguments[0]);
            if (element) {
                element.insertAdjacentHTML(arguments[1], arguments[2]);
            } else {
                throw new Error("Elemento não encontrado.");
            }
            """
            self.driver.execute_script(script, css_selector, position, html_string)
        except Exception as e:
            raise RuntimeError(f"Erro ao inserir HTML: {e}")

    def insert_script(self, script_content):
        """
        Insere um código JavaScript dentro da página carregada pelo Selenium e o executa.
        :param script_content: O conteúdo do script JavaScript a ser injetado e executado.
        """
        try:
            # Script para injetar um <script> com conteúdo especificado na página
            script = """
            var scriptTag = document.createElement('script');
            scriptTag.setAttribute('python-robot', '')
            scriptTag.innerHTML = arguments[0];  // Conteúdo do script a ser injetado
            document.body.appendChild(scriptTag);  // Ou insira no <head> caso prefira
            """

            # Executa o script no contexto do navegador através do Selenium
            self.driver.execute_script(script, script_content)
        except Exception as e:
            raise RuntimeError(f"Erro ao inserir script: {e}")

    def is_element_still_in_dom(self, element: WebElement):
        try:
            # Tentando acessar algo no elemento (como o texto ou atributo)
            tag_name = element.tag_name  # Apenas verificar se o acesso funciona
            return True  # Elemento ainda está anexado ao DOM
        except StaleElementReferenceException:
            return False  # Elemento não está mais anexado ao DOM

    def element_exist_in_dom(self, css_selector=None, xpath_selector=None, locator=None):
        if locator is None and css_selector is None and xpath_selector is None:
            raise Exception("Um dos parâmetros deve ser estabelecido.")

        if css_selector:
            locator=(By.CSS_SELECTOR, css_selector)
        if xpath_selector:
            locator=(By.XPATH, xpath_selector)

        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def alter_inner_html(self, element, html_string):
        """
        Altera o conteúdo HTML de um elemento contenteditable, substituindo seu innerHTML.

        :param element: O elemento cujo conteúdo HTML será alterado.
        :param html_string: A string de HTML que substituirá o conteúdo atual do elemento.
        """
        try:
            # Altera diretamente o conteúdo do innerHTML do elemento
            self.driver.execute_script("arguments[0].innerHTML = arguments[1];", element, html_string)
        except Exception as e:
            raise RuntimeError(f"Erro ao alterar innerHTML: {e}")

    def extract_text_as_json_from_element(self, locator=None, css_selector=None):
        """
        Extrai o texto de um elemento HTML localizado usando o tipo e valor do locator
        ou um seletor CSS, e tenta convertê-lo para JSON.

        :param locator: O localizador de tupla, podendo ser um tipo de localizador
                         (como By.ID, By.CLASS_NAME, etc.) e o valor correspondente.
                         Exemplo: (By.ID, 'element_id').
        :param css_selector: Um seletor CSS para localizar o elemento (exclusivo
                              se 'locator' não for fornecido).
                         Exemplo: '.example-class'.
        :return: O objeto JSON extraído, ou None se o texto não puder ser convertido para JSON.
        :raises ValueError: Se nenhum dos parâmetros locator ou css_selector for fornecido.
        :raises RuntimeError: Caso ocorra um erro ao tentar localizar o elemento ou ao converter o texto.

        **Comportamento:**
        - Se um locator for passado, ele deve ser uma tupla (tipo, valor), por exemplo:
          - `locator = (By.ID, 'some_id')`
          - `locator = (By.CLASS_NAME, 'some_class')`
        - Se um `css_selector` for passado, ele será tratado como um localizador do tipo `CSS_SELECTOR`.
        - O texto do elemento localizado será extraído e tentaremos convertê-lo para um JSON válido.
        - Se o texto não for JSON válido, será retornado `None`.
        """

        # Verificar se locator ou css_selector foi fornecido
        if not locator and not css_selector:
            raise ValueError("Você deve fornecer um 'locator' ou 'css_selector'.")

        # Se 'css_selector' for fornecido, construir locator
        if css_selector:
            locator = (By.CSS_SELECTOR, css_selector)

        try:
            # Localiza o elemento usando o tipo de localizador e o seletor fornecidos
            element = self.driver.find_element(*locator)

            # Obtém o texto do elemento
            text_content = element.text or element.get_attribute('innerText')

            # Tenta carregar o texto extraído como JSON
            try:
                json_data = json.loads(text_content)
                return json_data
            except json.JSONDecodeError:
                print("O texto extraído não é um JSON válido.")
                return None

        except Exception as e:
            raise RuntimeError(f"Erro ao extrair texto como JSON: {e}")