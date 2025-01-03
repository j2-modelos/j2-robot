import json
import os
import uuid
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from core.assistant import Assistant
from core.web_driver_manager import WebDriverManager
from model.driver_guia import DriverGuia
from model.j2_robot_erro import J2RobotErro
from utils.strings import extract_uuid


class ChatGpt:
    guia_alias = 'chatgpt'
    chatgpt_url = "https://chatgpt.com/"

    def __init__(self,  drivermgr: WebDriverManager, guia_compartilhada = True):
        self.drivemgr = drivermgr
        self.guia: DriverGuia = None
        self.guia_invocador_id = None
        self.guia_compartilhada = guia_compartilhada
        self.guia_alias = ChatGpt.guia_alias if guia_compartilhada else f"{ChatGpt.guia_alias}-{uuid.uuid1()}"

    async def init_async(self):
        driver = self.drivemgr.driver
        assistant = self.drivemgr.assistant
        url = os.getenv('CHAT_GPT_URL')

        self.guia_invocador_id = driver.current_window_handle
        if self.guia_compartilhada:
            self.guia = await  assistant.obter_guia(self.guia_alias)
            if self.guia is None:
                self.guia = await assistant.wait_abrir_nova_guia(url, self.guia_alias, 150)
                await assistant.wait_for_element_visible(css_selector='#prompt-textarea', timeout=60)
        else:
            self.guia = await assistant.wait_abrir_nova_guia(url, self.guia_alias , 150)
        self.drivemgr.driver.switch_to.window(self.guia_invocador_id)

    async def alternar(self):
        await  self.drivemgr.assistant.obter_guia(self.guia_alias)
        sleep(0.200)
        return self.guia

    async def voltar_guia_invocadora(self):
        if self.drivemgr.driver.current_window_handle == self.guia.id:
            self.drivemgr.driver.switch_to.window(self.guia_invocador_id)
        sleep(0.200)

    async def inserir_prompt(self, prompt: str):
        """
            Insere o prompt para o chat e envia a pergunta
        :param prompt: uma string que representa um simples arquivo html gerado
        :return:
        """
        assistant = self.drivemgr.assistant
        prompt_textarea = await assistant.wait_for_element_visible(css_selector='#prompt-textarea', timeout=60)
        assistant.dom_util.alter_inner_html(element=prompt_textarea, html_string=prompt)
        botao_enviar = await assistant.wait_for_element_visible(locator=(By.XPATH, "//*[@id='composer-background']/div[2]/button"), timeout=60)
        assistant.clicar_elemento(botao_enviar)

    async def aguardar_resposta(self, uuid_vinculada: str):
        """
            Aguarda o chatgpt responder pela json identificada pela uuid enviada.
        :return:
        """
        asst = self.drivemgr.assistant
        elemento_esperado_locator = (By.XPATH, f"//span[contains(text(), '{uuid_vinculada}')]/..")
        await asst.wait_for_element_exist(locator=elemento_esperado_locator, timeout=180)
        await asst.wait_for(lambda d: asst.dom_util.extract_text_as_json_from_element(locator=elemento_esperado_locator), 180)
        asst.clicar_elemento(locator=elemento_esperado_locator)
        resposta_json = asst.dom_util.extract_text_as_json_from_element(elemento_esperado_locator)
        return resposta_json

    async def iniciar_novo_chat(self, titulo_chat=None):
        asst = self.drivemgr.assistant

        await  self.alternar()

        url_atual = await asst.obter_url_frame_ativo()
        if url_atual != ChatGpt.chatgpt_url or not asst.dom_util.element_exist_in_dom(css_selector='#prompt-textarea'):
            async def esperar_mudar_url(_):
                ob_url = await asst.obter_url_frame_ativo()
                return url_atual != ob_url

            new_chat_acao = await asst.wait_for_element_exist((By.XPATH, "//div[text()='ChatGPT']//following-sibling::*//button"), timeout=60)
            asst.clicar_elemento(new_chat_acao)
            await asst.wait_for_async(esperar_mudar_url)
            #text_area = await assistant.wait_for_element_visible(css_selector="#prompt-textarea", timeout=60)

            #await assistant.wait_for_element_not_more_in_dom(text_area)
            #await assistant.wait_for_element_visible(css_selector="#prompt-textarea", timeout=60)

        uuid_gerado = str(uuid.uuid1())
        prompt_inicial = f'Vamos iniciar?{ f"Análise de { titulo_chat }." if titulo_chat else "" } Responda-me: "Ok, vamos lá!!!" e um json: {{ ID:{uuid_gerado} }}"'
        await self.inserir_prompt(prompt_inicial)
        _, __, resultado = await asst.wait_race([
            (self.aguardar_resposta(uuid_vinculada=uuid_gerado), "sucesso"),
            (asst.wait_for_element_visible(css_selector=".text-token-text-error"), "falha")
        ], timeout=190)

        if resultado == "sucesso":
            if titulo_chat:
                url_atual = await asst.obter_url_frame_ativo()
                menu_activator = await asst.wait_for_element_visible(locator=(By.XPATH, f"//nav//a[contains(@href, '{extract_uuid(url_atual)}')]/..//button"))
                asst.clicar_elemento(menu_activator)
                comando_renomear = await asst.wait_for_element_visible(locator=(By.XPATH, "//div[contains(text(),'Renomear')]"))
                asst.clicar_elemento(comando_renomear)
                input_chat_name = await asst.wait_for_element_visible(
                    locator=(By.XPATH, f"//nav//a[contains(@href, '{extract_uuid(url_atual)}')]/..//input"))
                asst.campo_limpar_e_escrever(input_chat_name, titulo_chat)
        else:
            await  self.voltar_guia_invocadora()
            raise J2RobotErro(7)
