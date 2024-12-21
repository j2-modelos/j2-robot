from selenium import webdriver

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