from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from core.web_driver_manager import WebDriverManager
from model.situacao_tarefa_enum import SituacaoTarefaEnum
from utils.mensagem import Mensagem
import re


class ListaProcessosTarefa:
    def __init__(self, driver: WebDriverManager, mensagem: Mensagem, ng_frame: WebElement):
        self.drivermgr = driver
        self.mensagem: Mensagem = mensagem
        self.ng_frame: WebElement = ng_frame

        self.ultimo_card_nao_conncluido: str = None

        print("ListaProcessosTarefa configurado.")

    async def esperar_transicao_do_frame_tarefa(self):
        try:
            self.drivermgr.driver.switch_to.default_content()
            self.drivermgr.driver.switch_to.frame(self.ng_frame)
            frame_tarefa = await self.drivermgr.assistant.wait_for_element_visible(
                locator=(By.XPATH, "//*[@id='frame-tarefa']"))
            self.drivermgr.driver.switch_to.frame(frame_tarefa)

            return frame_tarefa
        except Exception as e:
            print(f"Frame já Selecionado. {e}")

    async def alternar_para_frame_tarefa(self):
        try:
            self.drivermgr.driver.switch_to.default_content()
            self.drivermgr.driver.switch_to.frame(self.ng_frame)
            frame_tarefa = await self.drivermgr.assistant.wait_for_element_visible(
                locator=(By.XPATH, "//*[@id='frame-tarefa']"))
            self.drivermgr.driver.switch_to.frame(frame_tarefa)

            return frame_tarefa
        except Exception as e:
            print(f"Frame já Selecionado. {e}")

    def alternar_para_ng_frame(self):
        try:
            self.drivermgr.driver.switch_to.default_content()
            self.drivermgr.driver.switch_to.frame(self.ng_frame)
            #self.drivermgr._driver.switch_to.frame(0)
        except Exception as e:
            print(f"Frame já Selecionado. {e}")

    async def iterar_cards_pendentes(self):
        card = await self.obter_proximo_card()

        cards_pendentes = True
        while cards_pendentes:
            try:
                selecionador = card.find_element(By.CSS_SELECTOR, '.tarefa-numero-processo')
                numero_processo = self.dados_cartao(card)
                def assegurar_mudanca_tarefa(driver):
                    self.drivermgr.assistant.clicar_elemento(selecionador)
                    try:
                        driver.find_element(By.XPATH, f"//div[@id='frameTarefas']//a[contains(text(), '{numero_processo}')]")
                        return True
                    except:
                        return False

                await self.drivermgr.assistant.wait_for(assegurar_mudanca_tarefa, 60)

                await self.alternar_para_frame_tarefa()

                resultado_robo = await Movimentar(drivermgr=self.drivermgr, mensagem=self.mensagem, lista=self).movimentar_processo()

                self.alternar_para_ng_frame()

                if resultado_robo != SituacaoTarefaEnum.RESOLVIDA:
                    id_cartao = card.find_element(By.CSS_SELECTOR, ".hidden[id]").get_attribute("id")
                    self.ultimo_card_nao_conncluido = id_cartao
                    card = await self.obter_proximo_card(card, False)
                else:
                    card = await self.obter_proximo_card(card, True)

            except Exception as e:
                print(f"Iteração sobre cards da lista concluída. Motivo: {e}")
                cards_pendentes = False

    async def obter_proximo_card(self, card_atual = None, atual_deve_sair_da_lista: bool | None = None):
        asst = self.drivermgr.assistant
        if not self.ultimo_card_nao_conncluido and not card_atual:
            card = await asst.wait_for_element_visible(
                css_selector="p-datalist .ui-datalist-data processo-datalist-card", timeout=30)
            return card
        elif not self.ultimo_card_nao_conncluido and card_atual:
            await asst.wait_for_element_not_more_in_dom(card_atual)
            card = await self.obter_proximo_card()
            return card
        elif self.ultimo_card_nao_conncluido and card_atual:
            print(f'0. Deve sumir? {atual_deve_sair_da_lista}.')
            if atual_deve_sair_da_lista:
                print('1. Esperando card atual sumir.')
                await asst.wait_for_element_not_more_in_dom(card_atual)

            print(f'2. Experar o próximo elemento existir: depois de {self.ultimo_card_nao_conncluido}')
            try:
                asst.find_element(
                    locator=(By.XPATH,
                             f"//span[@id='{self.ultimo_card_nao_conncluido}']//ancestor::li[1]//following-sibling::li[1]//processo-datalist-card"))
            except Exception as e:
                print("2.1. Não existe próximo card")
                raise "Não existe o próximo card"

            print('3. esperar ficar visível.')
            proximo_cartao = await asst.wait_for_element_visible(
                locator=(By.XPATH, f"//span[@id='{self.ultimo_card_nao_conncluido}']//ancestor::li[1]//following-sibling::li[1]//processo-datalist-card"),
                timeout=30)
            print('4. Encontrado.')
            self.informacao_cartao(proximo_cartao)
            return proximo_cartao
        elif self.ultimo_card_nao_conncluido and not card_atual:
            raise "É possível mesmo que isso tenha ocorrido."
        else:
            raise "Ponto de execução não esperado."

    def informacao_cartao(self, cartao: WebElement):
        print(f"Este cartão: { self.dados_cartao(cartao)}")

    def dados_cartao(self, cartao: WebElement):
        padrao_processo = r"(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})"
        inner_html = cartao.get_attribute("innerHTML")
        resultado = re.search(padrao_processo, inner_html)
        numero_processo = resultado.group(1)
        return numero_processo


from pje.processo.movimentar import Movimentar