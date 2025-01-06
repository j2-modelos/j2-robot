import asyncio

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from core.web_driver_manager import WebDriverManager
from model.cartao_tarefa import CartaoTarefa
from model.j2_robot_erro import J2RobotErro
from model.situacao_tarefa_enum import SituacaoTarefaEnum
from model.mensagem import Mensagem
import re


class ListaProcessosTarefa:
    css_selector_primeiro_cartao_lista = "p-datalist .ui-datalist-data processo-datalist-card"

    def __init__(self, driver: WebDriverManager, mensagem: Mensagem, ng_frame: WebElement):
        self.drivermgr = driver
        self.mensagem: Mensagem = mensagem
        self.ng_frame: WebElement = ng_frame

        self.ultimo_card_nao_conncluido: CartaoTarefa = None

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

    async def exibir_aba_processos(self):
        asst = self.drivermgr.assistant

        aba_processos = await asst.wait_for_element_visible(css_selector="#myTabs a[href='#processosTarefa']")
        asst.clicar_elemento(aba_processos)

        return self

    async def iterar_cards_pendentes(self):
        card = await self.obter_proximo_card()
        asst = self.drivermgr.assistant

        while True:
            try:
                if await asst.verificar_modificacao_status_automacao():
                    print(f"Iteração sobre cards da lista concluída. Motivo: Parado pelo usuário")
                    break

                def assegurar_mudanca_tarefa(driver):
                    card.selecionar()
                    try:
                        driver.find_element(By.XPATH, f"//div[@id='frameTarefas']//a[contains(text(), '{card.numero_processo}')]")
                        return True
                    except:
                        return False

                await self.drivermgr.assistant.wait_for(assegurar_mudanca_tarefa, 60)

                await self.alternar_para_frame_tarefa()

                try:
                    resultado_robo = SituacaoTarefaEnum.ABERTA

                    #raise J2RobotErro(3)
                    resultado_robo = await Movimentar(drivermgr=self.drivermgr, mensagem=self.mensagem, lista=self).movimentar_processo()
                except J2RobotErro as e:
                    if e.codigo_erro in [7]:
                        print("A aplicação será encerrada")
                        raise J2RobotErro(8, complemento="Erro no Chat GPT")

                    if e.codigo_erro in [5, 3]:
                        #inserir aqui lógica para recarregar a lista, para eventualmente sair a tarefa que deu erro?????.
                        try:
                            await self.recarregar_lista_processos()
                        finally:
                            pass
                    resultado_robo = SituacaoTarefaEnum.FALHA
                except Exception as e:
                    raise e

                self.alternar_para_ng_frame()

                if await asst.verificar_modificacao_status_automacao():
                    print(f"Iteração sobre cards da lista concluída. Motivo: Parado pelo usuário")
                    break


                if resultado_robo == SituacaoTarefaEnum.FALHA:
                    if card.esta_anexao_ao_dom():
                        self.ultimo_card_nao_conncluido = card
                        card = await self.obter_proximo_card(card, False)
                    pass
                elif resultado_robo != SituacaoTarefaEnum.RESOLVIDA:
                    self.ultimo_card_nao_conncluido = card
                    card = await self.obter_proximo_card(card, False)
                else:
                    card = await self.obter_proximo_card(card, True)

            except Exception as e:
                print(f"Iteração sobre cards da lista concluída. Motivo: {e}")
                break

    async def recarregar_lista_processos(self):
        """
        Recarrega a lista de processos da tarefa por meio da estratégia clicar no botão ativador do filtro do componente.

        :return:Uma corrotina que resolve para um valor booleano, indicando
                True se a lista foi recarregada e possui cartões e
                False se não possui cartões
        :rtype: Future[bool]
        """
        asst = self.drivermgr.assistant
        css_selector_prim_cart = ListaProcessosTarefa.css_selector_primeiro_cartao_lista
        timeout = 30

        self.alternar_para_ng_frame()

        ativador = await self.drivermgr.assistant.wait_for_element_exist(css_selector="#filtro-tarefas + button")

        try:
            if asst.dom_util.element_exist_in_dom(css_selector_prim_cart):
                primeiro_cartao = asst.find_element(css_selector=css_selector_prim_cart)
                asst.clicar_elemento(ativador)
                await asst.wait_for_element_not_more_in_dom(primeiro_cartao)
                _, __, resultado = await asst.wait_race(timeout=timeout, tasks=[
                    (asst.wait_for_element_visible(css_selector=css_selector_prim_cart, timeout=timeout), True),
                    (asst.wait_for_element_visible(css_selector='div.ui-datalist-emptymessage', timeout=timeout), False)
                ])
                return resultado
            else:
                try:
                    menasgem_vazia = asst.find_element(css_selector='div.ui-datalist-emptymessage')
                    asst.clicar_elemento(ativador)
                    await asst.wait_for_element_not_more_in_dom(menasgem_vazia)
                    await asst.wait_for_element_visible(css_selector=css_selector_prim_cart)
                    return True

                except asyncio.TimeoutError as e:
                    print("Timeout para sinalizador mensagens vazia desaparecer")
                    return False

        except asyncio.TimeoutError as e:
            print(f"Exceção: {e}")
            raise J2RobotErro(4)

    async def obter_proximo_card(self, card_atual = None, atual_deve_sair_da_lista: bool | None = None):
        asst = self.drivermgr.assistant
        if not self.ultimo_card_nao_conncluido and not card_atual:
            await asst.wait_for_element_visible(
                css_selector="p-datalist .ui-datalist-data processo-datalist-card .tarefa-numero-processo", timeout=30)
            card = await asst.wait_for_element_visible(
                css_selector="p-datalist .ui-datalist-data processo-datalist-card", timeout=30)
            return CartaoTarefa(card, self.drivermgr)
        elif not self.ultimo_card_nao_conncluido and card_atual:
            await card_atual.esperar_nao_estar_mais_no_dom()
            card = await self.obter_proximo_card()
            return card
        elif self.ultimo_card_nao_conncluido and card_atual:
            print(f'0. Deve sumir? {atual_deve_sair_da_lista}.')
            if atual_deve_sair_da_lista:
                print('1. Esperando card atual sumir.')
                await card_atual.esperar_nao_estar_mais_no_dom()

            print(f'2. Experar o próximo elemento existir: depois de {self.ultimo_card_nao_conncluido}')
            try:
                asst.find_element(
                    locator=(By.XPATH,
                             f"//span[@id='{self.ultimo_card_nao_conncluido.id_tarefa}']//ancestor::li[1]//following-sibling::li[1]//processo-datalist-card"))
            except Exception as e:
                print("2.1. Não existe próximo card")
                raise "Não existe o próximo card"

            print('3. esperar ficar visível.')
            proximo_cartao = await asst.wait_for_element_visible(
                locator=(By.XPATH, f"//span[@id='{self.ultimo_card_nao_conncluido.id_tarefa}']//ancestor::li[1]//following-sibling::li[1]//processo-datalist-card"),
                timeout=30)
            print('4. Encontrado.')
            self.informacao_cartao(proximo_cartao)
            return CartaoTarefa(proximo_cartao, self.drivermgr)
        elif self.ultimo_card_nao_conncluido and not card_atual:
            raise J2RobotErro(6, complemento="situação dos cartões não é esperada.")
        else:
            raise J2RobotErro(6, complemento="Ponto de execução não esperado em obter_proximo_card")

    def informacao_cartao(self, cartao: WebElement):
        print(f"Este cartão: { self.dados_cartao(cartao)}")

    def dados_cartao(self, cartao: WebElement):
        padrao_processo = r"(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})"
        inner_html = cartao.get_attribute("innerHTML")
        resultado = re.search(padrao_processo, inner_html)
        numero_processo = resultado.group(1)
        return numero_processo


from pje.processo.movimentar import Movimentar