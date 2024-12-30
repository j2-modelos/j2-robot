# Classe base (superclasse)
from time import sleep

from core.web_driver_manager import WebDriverManager
from fluxo.core.tarefa_fluxo import TarefaFluxo
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from utils.mensagem import Mensagem


class AvaliarMultiSelecao(TarefaFluxo):
    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa):
        TarefaFluxo.__init__(self, nome, drivermgr, mensagem, painel_lista)

    async def tarefa_esta_pronta(self):
        await super().tarefa_esta_pronta()

        await self.drivermgr.ast().wait_for_element_exist(css_selector='#taskInstanceForm')
        await self.drivermgr.ast().wait_for_element_exist(css_selector='.propertyView ')
        await self.drivermgr.ast().wait_for_element_exist(css_selector= "[id*='visualizarDecisao']")
