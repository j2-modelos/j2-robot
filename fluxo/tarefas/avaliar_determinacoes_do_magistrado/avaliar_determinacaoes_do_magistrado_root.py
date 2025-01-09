import uuid
from pathlib import Path
from string import Template
from time import sleep

from chatgpt.chatgpt import ChatGpt
from core.web_driver_manager import WebDriverManager
from fluxo.core.executor_tabela_decisao import ExecutorTabelaDecisao
from fluxo.tarefas.classes.avaliacao_multi_selecao import AvaliarMultiSelecao
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from model.j2_robot_erro import J2RobotErro
from model.mensagem import Mensagem
from utils.path import get_resource_path


class AvaliarDeterminacoesDoMagistrado(AvaliarMultiSelecao, ExecutorTabelaDecisao):

    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa):
        nome_ = "Avaliar determinações do magistrado"
        AvaliarMultiSelecao.__init__(self, nome_, drivermgr, mensagem, painel_lista)

        caminho_tabela_decisao = get_resource_path("fluxo/tarefas/avaliar_determinacoes_do_magistrado/avaliar_determinacoes_do_magistrado_tabela_decisao.xlsx", packaged=False)
        ExecutorTabelaDecisao.__init__(self, nome_, drivermgr, mensagem, painel_lista,
                                       caminho_tabela_decisao, 3, True, prompt=True )

        self.chatgpt: ChatGpt = None



    async def tarefa_esta_pronta(self):
        if self.esta_pronta:
            return
        #carregar guia chatgpt ou reutilizar
        await super().tarefa_esta_pronta()
        self.chatgpt  = ChatGpt(drivermgr=self.drivermgr, guia_compartilhada=True)
        await self.chatgpt.init_async()
        await  self.painel_lista.alternar_para_frame_tarefa()

    async  def realizar_tarefa(self):
        await self.tarefa_esta_pronta()
        self.esta_pronta = True
        await super().realizar_tarefa()
        #aqui poderia ser encadeado uma outra tarefa de fluxo??????????

        ato_judicial = self.obter_teor_ato_judicial_para_prompt()
        gen_uuid = str(uuid.uuid1())
        ato_uuid = self.obter_uuid_ato_judicial() or "[inexistente]"
        """
        with open(str(Path(__file__).parent / 'avaliar_determinacoes_do_magistrado_prompt.html'), "r", encoding="utf-8") as arquivo:
            prompt = Template(arquivo.read())

        dados = {
            "ato_judicial": ato_judicial,
            "uuid": gen_uuid,
            "ato_uuid": ato_uuid
        }
        prompt = prompt.substitute(dados)
        """
        chat_name = f"{self.obter_acronimo_tarefa()} {self.numero_processo or "XXXXXXX-XX.XXXX.X.XX.XXXX"}"
        prompt = self.prompt.obter_compilado( json_base={
            "uuid": gen_uuid,
            "ato_uuid": ato_uuid,
            "numero": self.numero_processo
        }, substitutos= {
            "ato_judicial": ato_judicial,
        } )

        try:
            await self.chatgpt.iniciar_novo_chat(chat_name)
            await self.chatgpt.inserir_prompt(prompt)
            resposta_json = await self.chatgpt.aguardar_resposta(gen_uuid)
        except J2RobotErro as e:
            if e.codigo_erro == 7:
                await  self._sinalizar_erro("CHAT GPT ERRO")
            raise e

        print("A resposta do chatgpt foi:")
        print(resposta_json)
        await self.chatgpt.voltar_guia_invocadora()
        await  self.painel_lista.alternar_para_frame_tarefa()

        sleep(1)

        self.json_para_analise = resposta_json

        self.decidir()
        await self._sinalizar_automacao()
        await self.executar_medidas_a_tomar()

        return self.situacao
