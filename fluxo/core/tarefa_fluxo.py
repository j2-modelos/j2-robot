# Classe base (superclasse)
from time import sleep


from core.web_driver_manager import WebDriverManager
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from services.etiqueta_servico import EtiquetaServico
from utils.mensagem import Mensagem
from selenium.webdriver.common.by import By
from model.situacao_tarefa_enum import SituacaoTarefaEnum
from utils.strings import criar_acronimo
from typing import Tuple


class TarefaFluxo():
    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa):
        self.nome = nome
        self.drivermgr = drivermgr
        self.mensagem = mensagem
        self.painel_lista = painel_lista
        self.tablea_decisao = None
        self.situacao = SituacaoTarefaEnum.ABERTA
        self.etiqueta_servico = EtiquetaServico(drivermgr.driver)

    async def tarefa_esta_pronta(self):
        sleep(0.250)
        await self.drivermgr.ast().wait_for_chrome_ready()

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
        frame_tarefa = await self.drivermgr.assistant.wait_for_element_visible(
            locator=(By.XPATH, "//*[@id='frame-tarefa']"))
        src_atual = frame_tarefa.get_attribute('src')
        encaminhar_botao = await asst.wait_for_element_visible(css_selector="#btnTransicoesTarefa")
        asst.clicar_elemento(encaminhar_botao)
        transicao = await asst.wait_for_element_visible(locator=(By.XPATH, f"//a[text()='{transicao}']"))
        asst.clicar_elemento(transicao)
        def mudanca_src_frame(drive):
            return frame_tarefa.get_attribute('src') != src_atual
        await asst.wait_for(mudanca_src_frame)
        await  self.painel_lista.alternar_para_frame_tarefa()
        print(f"Transição de tarefa para '{transicao}'")

    async def carregar_tabela_decisao(self, caminha_arquivo: str, niveis_dados: int):
        self.tablea_decisao = pd.read_excel(caminha_arquivo)

    async def inserir_etiqueta_processo(self, etiqueta):
        id_processo = await self.drivermgr.assistant.obter_parametro_url('idProcesso')
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
        id_processo = await self.drivermgr.assistant.obter_parametro_url('idProcesso')
        return self.etiqueta_servico.inserir_subetiqueta_processo(
            id_processo=id_processo,
            subetiqueta=subetiqueta,
            etiqueta_pai=etiqueta_pai
        )
