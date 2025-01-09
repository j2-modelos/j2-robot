import asyncio

from core.web_driver_manager import WebDriverManager
from fluxo.core.tarefa_fluxo import TarefaFluxo
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from model.mensagem import Mensagem
from utils.strings import transformar_em_nome_classe


class Movimentar:
    def __init__(self, drivermgr: WebDriverManager, mensagem: Mensagem, lista: ListaProcessosTarefa):
        self.mensagem: Mensagem = mensagem
        classe_tarefa = globals().get(transformar_em_nome_classe(mensagem.tarefa))

        if classe_tarefa and issubclass(classe_tarefa, TarefaFluxo):
            self.tarefa_fluxo = classe_tarefa(mensagem.tarefa, drivermgr, mensagem, lista)
        else:
            raise ValueError(f"Tarefa '{mensagem.tarefa}' não encontrada ou não é válida.")

        self.drivermgr = drivermgr
        self.painel_lista = lista
        self.pronto = False

        asyncio.create_task( self.init_async() )

    async  def movimentar_processo(self):
        def esta_pronto(driver):
            return  self.pronto

        try:
            await self.drivermgr.assistant.wait_for_and_state_controller(esta_pronto)
        except Exception as e:
            print(e)

        resultado = await  self.tarefa_fluxo.realizar_tarefa()
        return resultado

    async def init_async(self):
        self.pronto = True


from fluxo.tarefas.avaliar_determinacoes_do_magistrado.avaliar_determinacaoes_do_magistrado_root import AvaliarDeterminacoesDoMagistrado