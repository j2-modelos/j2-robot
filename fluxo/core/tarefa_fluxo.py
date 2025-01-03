# Classe base (superclasse)
import re
import asyncio
from time import sleep


from core.web_driver_manager import WebDriverManager
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from services.etiqueta_servico import EtiquetaServico
from services.processo_servico import ProcessoServico
from model.mensagem import Mensagem
from selenium.webdriver.common.by import By
from model.situacao_tarefa_enum import SituacaoTarefaEnum
from utils.strings import criar_acronimo
from typing import Tuple
from model.j2_robot_erro import J2RobotErro


class TarefaFluxo():
    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa):
        self.nome = nome
        self.drivermgr = drivermgr
        self.mensagem = mensagem
        self.painel_lista = painel_lista
        self.tablea_decisao = None
        self.situacao = SituacaoTarefaEnum.ABERTA
        self.etiqueta_servico = EtiquetaServico(drivermgr.driver)
        self.processo_servico = ProcessoServico(drivermgr.driver)
        self.id_processo = None
        self.id_tarefa = None
        self.numero_processo = None
        self.esta_pronta = False #evitar dupla chamada para classes de fluxo polimórficas

        asyncio.create_task(self._init_async())

    async def _init_async(self):
        asst = self.drivermgr.assistant

        if self.id_tarefa and self.id_processo and self.numero_processo:
            return

        self.id_tarefa = await asst.obter_parametro_url("newTaskId")
        self.id_processo = await asst.obter_parametro_url("idProcesso")
        dados_basico = self.processo_servico.obter_dados_basicos(self.id_processo)
        if "numeroProcesso" in dados_basico:
            self.numero_processo = dados_basico["numeroProcesso"]

        return

    async def tarefa_esta_pronta(self):
        if self.esta_pronta:
            return

        sleep(0.250)
        await self.drivermgr.ast().wait_for_chrome_ready()
        esta_saudavel = await self.frame_tarefa_esta_saudavel()
        if not esta_saudavel:
            raise J2RobotErro(5)

    def obter_acronimo_tarefa(self):
        return criar_acronimo(self.nome)

    async def _sinalizar_automacao(self, complemento: Tuple[str, str] = None):
        acronimo = criar_acronimo(self.nome)
        sinal = f"[#] {acronimo}"
        await  self.inserir_etiqueta_processo(sinal)
        if complemento:
            id, text = complemento
            await  self.inserir_etiqueta_processo(f"[#][{id}] {text}")

        return sinal


    async  def realizar_tarefa(self):
        await self.tarefa_esta_pronta()

        print(f"Realizando tarefa{self.nome}. Mensagem recebida: {self.mensagem}")

    async def fluir_para_transicao(self, transicao: str):
        asst = self.drivermgr.assistant
        self.painel_lista.alternar_para_ng_frame()

        try:
            frame_tarefa = await self.drivermgr.assistant.wait_for_element_visible(
                locator=(By.XPATH, "//*[@id='frame-tarefa']"), timeout=30)
            src_atual = frame_tarefa.get_attribute('src')
            encaminhar_botao = await asst.wait_for_element_visible(css_selector="#btnTransicoesTarefa")
            asst.clicar_elemento(encaminhar_botao)
            transicao = await asst.wait_for_element_visible(locator=(By.XPATH, f"//a[text()='{transicao}']"))
            asst.clicar_elemento(transicao)

            async def mudanca_src_frame(drive):
                src_mudou = frame_tarefa.get_attribute('src') != src_atual
                nao_esta_mais_no_dom = not asst.dom_util.is_element_still_in_dom(frame_tarefa)
                frame_nao_esta_saudavel = not await self.frame_tarefa_esta_saudavel()
                self.painel_lista.alternar_para_ng_frame()

                if nao_esta_mais_no_dom:
                    raise J2RobotErro(1)
                if frame_nao_esta_saudavel:
                    raise J2RobotErro(2)
                return src_mudou

            await asst.wait_for_async(mudanca_src_frame)
            print(f"Transição de tarefa para '{transicao}'")
            await  self.painel_lista.alternar_para_frame_tarefa()

        except J2RobotErro as e:
            print(f"FALHA na transição de tarefa para '{transicao}': {e}")
            if e.codigo_erro == 1 or e.codigo_erro == 2:
                raise J2RobotErro(3, e)
            else:
                raise Exception("Erro desconhecido.")
        except Exception as e:
            print(f"FALHA na transição de tarefa para '{transicao}': {e}")
            raise f"#003: Erro durante a transição da tarefa pelo fluxo.{e}"



    async def frame_tarefa_esta_saudavel(self):
        """
        Considera-se que o contexto inicial é ListaProcessoTarefa no ngFrame de dev.seam
        :return:
        """
        await self.painel_lista.alternar_para_frame_tarefa()
        url_frame = await  self.drivermgr.assistant.obter_url_frame_ativo()
        resultado = True

        if re.search(r'(error|errorMovimentarFluxo)\.seam', url_frame):
            resultado = False

        return resultado

    async def inserir_etiqueta_processo(self, etiqueta):
        id_processo = self.id_processo or await self.drivermgr.assistant.obter_parametro_url('idProcesso')
        return self.etiqueta_servico.inserir_etiqueta_processo(id_processo=id_processo, etiqueta=etiqueta)


    async def inserir_subetiqueta_processo(self, subetiqueta, etiqueta_pai):
        """
        Associa uma subetiqueta a um processo, vinculando-a a uma etiqueta pai existente.

        Parâmetros:
        ----------
        subetiqueta : str
            Nome da subetiqueta a ser adicionada.
        etiqueta_pai : str
            Nome completo da etiqueta pai (formato: "Categoria > Subcategoria").

        Retorno:
        -------
        async : any
            Resultado assíncrono da operação.

        Notas:
        ------
        - O ID do processo é obtido da URL atual via `idProcesso`.
        - `etiqueta_pai` deve estar no formato correto para sucesso da operação.
        """
        id_processo = self.id_processo or await self.drivermgr.assistant.obter_parametro_url('idProcesso')
        return self.etiqueta_servico.inserir_subetiqueta_processo(
            id_processo=id_processo,
            subetiqueta=subetiqueta,
            etiqueta_pai=etiqueta_pai
        )
