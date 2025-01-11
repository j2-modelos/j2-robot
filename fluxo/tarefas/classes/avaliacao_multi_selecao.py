# Classe base (superclasse)

from selenium.webdriver.common.by import By

from core.web_driver_manager import WebDriverManager
from fluxo.core.tarefa_fluxo import TarefaFluxo
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from model.mensagem import Mensagem
from utils.env import ENV_AVALIACAO_MULTI_SELECAO_MODO_VALIDACAO


class AvaliarMultiSelecao(TarefaFluxo):
    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa):
        TarefaFluxo.__init__(self, nome, drivermgr, mensagem, painel_lista)

    async def tarefa_esta_pronta(self):
        await super().tarefa_esta_pronta()
        if self.esta_pronta:
            return

        await self.drivermgr.ast().wait_for_element_exist(css_selector='#taskInstanceForm')
        await self.drivermgr.ast().wait_for_element_exist(css_selector='.propertyView ')
        await self.drivermgr.ast().wait_for_element_exist(css_selector= "[id*='visualizarDecisao']")

    def obter_teor_ato_judicial_para_prompt(self):
        try:
            # Localizar o elemento pelo seletor CSS e obter o texto
            elemento = self.drivermgr.driver.find_element(By.CSS_SELECTOR, "#paginaInteira")
            texto_completo = elemento.text

            # Verificar se o tamanho do texto é menor ou igual a 5000
            if len(texto_completo) <= 5000:
                return texto_completo

            # Encontrar a última ocorrência da palavra 'dispositivo' no texto
            palavra = "dispositivo"
            indice = texto_completo.lower().rfind(palavra)

            if indice != -1:
                # Extrair o conteúdo do índice da última palavra até o final
                texto_completo_dispositivo = texto_completo[indice + len(palavra):].strip()
                texto_completo_inicial = texto_completo[:indice].strip()

                # Limitar o tamanho da parte inicial para que a concatenação com a parte do dispositivo não ultrapasse 5000 caracteres
                tamanho_inicial = 5000 - len(texto_completo_dispositivo)

                if len(texto_completo_inicial) > tamanho_inicial:
                    texto_completo_inicial = texto_completo_inicial[:tamanho_inicial] + "(...)"

                # Concatenar a parte inicial e a do dispositivo
                texto_final = texto_completo_inicial + texto_completo_dispositivo
                return texto_final
            else:
                # Se a palavra 'dispositivo' não for encontrada, retorna os últimos 5000 caracteres
                return texto_completo[-5000:] if len(texto_completo) > 5000 else texto_completo

        except Exception as e:
            return f"Erro ao tentar processar o texto: {e}"

    def obter_uuid_ato_judicial(self):
        """
        Obtem o uuid vinculado ao ato judicial vinculado a tarefa atual.

        Essa função está associado a integrações realizados por j2Modelos.

        :return: O uuid vinculado ao to judicial ou None
        """
        uuid_value = None
        try:
            uuid_input_j2_modelos = self.drivermgr.driver.find_element(By.CSS_SELECTOR, "#j2Data\\.guid")
            uuid_value = uuid_input_j2_modelos.get_attribute("value")
        finally:
            return uuid_value

    async def selecionar_tarefa_nodo(self, tarefa):
        if ENV_AVALIACAO_MULTI_SELECAO_MODO_VALIDACAO:
            return

        x_path_query = f"//form[@id='taskInstanceForm']//label[normalize-space(text())='{tarefa}']/ancestor::div[contains(@class, 'propertyView')]//input"
        asst = self.drivermgr.assistant
        input_node = await asst.wait_for_element_exist(locator=(By.XPATH, x_path_query), timeout=60)
        input_node.click()
        return
