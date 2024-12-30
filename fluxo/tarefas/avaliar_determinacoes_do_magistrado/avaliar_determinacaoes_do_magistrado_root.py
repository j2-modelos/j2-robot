import random
import uuid
from pathlib import Path
from string import Template
from struct import pack_into
from time import sleep

from selenium.webdriver.common.by import By

from chatgpt.chatgpt import ChatGpt
from core.web_driver_manager import WebDriverManager
from fluxo.core.executor_tabela_decisao import ExecutorTabelaDecisao
from fluxo.tarefas.classes.avaliacao_multi_selecao import AvaliarMultiSelecao
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from utils.mensagem import Mensagem


class AvaliarDeterminacoesDoMagistrado(AvaliarMultiSelecao, ExecutorTabelaDecisao):

    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa):
        nome_ = "Avaliar determinações do magistrado"
        AvaliarMultiSelecao.__init__(self, nome_, drivermgr, mensagem, painel_lista)

        caminho_tabela_decisao = str(Path(__file__).parent / 'avaliar_determinacoes_do_magistrado_tabela_decisao.xlsx')
        ExecutorTabelaDecisao.__init__(self, nome_, drivermgr, mensagem, painel_lista,
                                       caminho_tabela_decisao, 3, True )

        self.chatgpt: ChatGpt = None



    async def tarefa_esta_pronta(self):
        #carregar guia chatgpt ou reutilizar
        await super().tarefa_esta_pronta()
        self.chatgpt  = ChatGpt(drivermgr=self.drivermgr, guia_compartilhada=True)
        await self.chatgpt.init_async()
        await  self.painel_lista.alternar_para_frame_tarefa()

    async  def realizar_tarefa(self):
        await self.tarefa_esta_pronta()
        await super().realizar_tarefa()
        #aqui poderia ser encadeado uma outra tarefa de fluxo??????????

        ato_judicial = self.obter_teor_ato_judicial_para_prompt()
        gen_uuid = str(uuid.uuid1())

        with open(str(Path(__file__).parent / 'avaliar_determinacoes_do_magistrado_prompt.html'), "r", encoding="utf-8") as arquivo:
            prompt = Template(arquivo.read())

        dados = {
            "atojudicial": ato_judicial,
            "guid": gen_uuid,
        }
        prompt = prompt.substitute(dados)

        await self.chatgpt.alternar()
        await self.chatgpt.inserir_prompt(prompt)
        resposta_json = await self.chatgpt.aguardar_resposta(gen_uuid)

        print("A resposta do chatgpt foi:")
        print(resposta_json)
        await self.chatgpt.voltar_guia_invocadora()
        await  self.painel_lista.alternar_para_frame_tarefa()

        sleep(1)

        self.json_para_analise = resposta_json

        self.decidir()
        await self.executar_medidas_a_tomar()
        await self._sinalizar_automacao()

        return self.situacao

    def obter_teor_ato_judicial_para_prompt(self):
        try:
            # Localizar o elemento pelo seletor CSS e obter o texto
            elemento = self.drivermgr.driver.find_element(By.CSS_SELECTOR, "#paginaInteira")
            texto_completo = elemento.text

            # Encontrar a última ocorrência da palavra 'dispositivo' no texto
            palavra = "dispositivo"
            indice = texto_completo.lower().rfind(palavra)

            if indice != -1:
                # Extrair o conteúdo do índice da última palavra até o final
                texto_extraido = texto_completo[indice + len(palavra):].strip()
                return texto_extraido
            else:
                # Se a palavra não foi encontrada, retorna os últimos 5000 caracteres (se houver)
                return texto_completo[-5000:] if len(texto_completo) > 5000 else texto_completo
        except Exception as e:
            return f"Erro ao tentar processar o texto: {e}"
