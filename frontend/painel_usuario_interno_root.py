from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from core.web_driver_manager import WebDriverManager
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from model.mensagem import Mensagem


class PainelUsuarioInterno:
    def __init__(self, drivermgr: WebDriverManager, ng_frame: WebElement):
        self.drivermgr = drivermgr
        self.ng_frame = ng_frame
        print("Painel Usuário Interno configurado.")

    def alternar_para_ng_frame(self):
        try:
            self.drivermgr.driver.switch_to.default_content()
            self.drivermgr.driver.switch_to.frame(self.ng_frame)
            #self.drivermgr._driver.switch_to.frame(0)
        except Exception as e:
            print(f"Frame já Selecionado. {e}")
        #finally:
            #self.drivermgr._driver.implicitly_wait(0.050)


    async  def ir_tela_inicial(self):
        self.alternar_para_ng_frame()
        li_a_home = await self.drivermgr.assistant.wait_for_element_visible(
            locator=(By.XPATH, "//li[@id='liHome']//a"))
        self.drivermgr.assistant.clicar_elemento(li_a_home)

    async def abrir_tarefa(self, mensagem: Mensagem):
        await  self.ir_tela_inicial()

        xpath = f"//right-panel//div[normalize-space(text())='Tarefas']//..//div[@id='divTarefasPendentes']//a[descendant::span[text() ='{mensagem.tarefa}']]"
        tarefa = await self.drivermgr.assistant.wait_for_element_visible(
            locator=(By.XPATH, xpath))
        self.drivermgr.assistant.clicar_elemento(tarefa)

        lista_processos_tarefa = ListaProcessosTarefa(self.drivermgr, mensagem, self.ng_frame)
        await lista_processos_tarefa.exibir_aba_processos()
        await lista_processos_tarefa.iterar_cards_pendentes()

        print('Ação executada')