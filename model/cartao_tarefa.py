import re
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from core.web_driver_manager import WebDriverManager
from model.j2_robot_erro import J2RobotErro


class CartaoTarefa:
    def __init__(self, web_element: WebElement, drivemgr: WebDriverManager):
        """
        Inicializa o extrator com um elemento web, extraindo o número do processo e o id da tarefa.

        :param web_element: WebElement fornecido pelo Selenium
        """
        self.web_element = web_element
        self.drivemgr = drivemgr
        self.numero_processo = self._extrair_numero_processo()
        self.id_tarefa = self._extrair_id_tarefa()

        #todo: neste ponto, o cartão pode estar mal formado e será necessário lançar uma exceção

    def _extrair_numero_processo(self):
        """
        Extrai o número único do processo com base na expressão regular predefinida.

        :return: O número do processo encontrado ou None se não encontrado.
        """
        regexp = r"\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}"
        texto_cartao = self.web_element.text
        match = re.search(regexp, texto_cartao)
        return match.group(0) if match else None

    def _extrair_id_tarefa(self):
        """
        Extrai o id da tarefa a partir de um elemento oculto com o seletor CSS ".hidden[id]".

        :return: O valor do atributo "id" ou None se o elemento não for encontrado.
        """
        try:
            elemento_oculto = self.web_element.find_element(By.CSS_SELECTOR, ".hidden[id]")
            return elemento_oculto.get_attribute("id")
        except Exception:
            return None

    def selecionar(self):
        """
        Procura o elemento responsável por selecionar a tarefa para execução e o clica.

        :return: O WebElement correspondente ou None se o elemento não for encontrado.
        """
        seletor_tarefa = self.web_element.find_element(By.CSS_SELECTOR, ".tarefa-numero-processo")
        main_div = self.web_element.find_element(By.CSS_SELECTOR, "div.datalist-content")
        self.drivemgr.assistant.clicar_elemento(seletor_tarefa)
        self.drivemgr.assistant.scroll_intoview(main_div)
        return seletor_tarefa

    def esta_anexao_ao_dom(self):
        """
        Verifica se o cartão ainda está anexado ao DOM, caso não esteja, verifica se há um clone
        do cartão e atribui a nova a referência ao próprio cartão.

        :return: boolean
        """
        esta_no_dom =  self.drivemgr.assistant.dom_util.is_element_still_in_dom(self.web_element)
        if esta_no_dom:
            return True
        else:
            try:
                elemento_oculto = self.drivemgr.driver.find_element(By.CSS_SELECTOR, f".hidden[id='{self.id_tarefa}']")
                cartao_clone = elemento_oculto.find_element(By.XPATH, "//ancestor::processo-datalist-card[1]")
                self.web_element = cartao_clone
                return True
            except:
                return False

    async def esperar_nao_estar_mais_no_dom(self):
        await self.drivemgr.assistant.wait_for_element_not_more_in_dom(self.web_element)

    def __str__(self):
        """
        Representa o objeto como uma string no formato "numero_processo | id_tarefa".

        :return: Uma string com os dados do número do processo e ID da tarefa.
        """
        return f"{self.numero_processo or 'N/A'} | {self.id_tarefa or 'N/A'}"
