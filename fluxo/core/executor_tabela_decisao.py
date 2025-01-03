from core.web_driver_manager import WebDriverManager
from fluxo.core.tarefa_fluxo import TarefaFluxo
from frontend.painel_usuario_interno.lista_processos_tarefa import ListaProcessosTarefa
from model.situacao_tarefa_enum import SituacaoTarefaEnum
from services.resolutor_tabela_decisao import ResolutorTabelaDecisao
from model.mensagem import Mensagem


class ExecutorTabelaDecisao(TarefaFluxo):
    tabelas_decisao = []

    def __init__(self, nome: str, drivermgr: WebDriverManager, mensagem: Mensagem, painel_lista: ListaProcessosTarefa,
                       caminho_arquivo: str, json_niveis: int, transpor=False, cabecalho=None):
        super().__init__(nome,drivermgr,mensagem, painel_lista)

        resolutor_deste = None
        for it_tarefa, it_resolutor in ExecutorTabelaDecisao.tabelas_decisao:
            if it_tarefa == self.nome:
                resolutor_deste = it_resolutor
                break

        if not resolutor_deste:
            resolutor_deste = ResolutorTabelaDecisao(caminho_tabela=caminho_arquivo, json_niveis=json_niveis, precisa_transpor=transpor, cabecalho=cabecalho)
            ExecutorTabelaDecisao.tabelas_decisao.append((self.nome, resolutor_deste ))


        self.resolutor = resolutor_deste
        self.json_para_analise = None
        self.medidas_a_tomar = None

    def decidir(self):
        #await  self.tarefa.fluir_para_transicao("Prosseguir")
        #self.decisao = "com pendencia"
        self.situacao = SituacaoTarefaEnum.EM_ANALISE
        self.resolutor.decidir(self.json_para_analise)

        if self.resolutor.estado_resolucao == "erro":
            print("Nenhuma decisão tomada após analise da tabela")
            self.situacao = SituacaoTarefaEnum.NAO_RESOLVIDA
        else:
            print("Decisão tomada via tabela de decisão")
            print(self.obter_decisao())
            self.situacao = SituacaoTarefaEnum.ANALISADA
            self.medidas_a_tomar = self.resolutor.medida_a_tomar

        return self.situacao

    def obter_situacao(self):
        return self.situacao

    async def executar_medidas_a_tomar(self):
        if self.obter_situacao() != SituacaoTarefaEnum.ANALISADA:
            return

        if len(self.medidas_a_tomar) == 0:
            print("Não existem mediads a tomar nesta execução.")
            self.situacao = SituacaoTarefaEnum.RESOLVIDA
            return

        print("Executando medidas para decisões de identificadores: ", self.resolutor.identificadores)
        try:
            for medida in self.medidas_a_tomar:
                for acao, passos in medida.items():
                    # Obtendo o método dinamicamente
                    metodo_da_acao = getattr(self, acao, None)

                    if callable(metodo_da_acao):  # Verifica se o método existe
                        for passo in passos:  # Itera pelos passos
                            await metodo_da_acao(passo)  # Passa o passo como argumento
                    else:
                        print(f"Método '{acao}' não encontrado!")

            if self._resolucao_por_fallback():
                self.situacao = SituacaoTarefaEnum.FALLBACK
            else:
                self.situacao = SituacaoTarefaEnum.RESOLVIDA
        except Exception as e:
            print(f"Erro na execução das medidas: {e}")
            await  self._sinalizar_erro()
            self.situacao = SituacaoTarefaEnum.FALHA
            raise e
    async def _sinalizar_erro(self, label_erro:str =None):
        await  self.inserir_subetiqueta_processo(etiqueta_pai=f"[#] {self.obter_acronimo_tarefa()}",
                                                 subetiqueta=f"[!] { label_erro if not label_erro is None else 'ERRO'}")

    def _resolucao_por_fallback(self):
        return True if ResolutorTabelaDecisao.rotulo_fallback_identificador in self.resolutor.identificadores else False


    def obter_decisao(self):
        return  {
            "situacao": self.situacao,
            "medidas_a_tomar": self.medidas_a_tomar,
            "identificadores": self.resolutor.identificadores,
            "json_para_analise": self.json_para_analise
        }

    async def _sinalizar_automacao(self):
        sinal = await super()._sinalizar_automacao()

        ids_list = self.resolutor.identificadores
        if not ids_list is None and len(ids_list) > 0:
            sinal_identificadores = f"[@] { ', '.join(ids_list) }"
            await self.inserir_subetiqueta_processo(subetiqueta=sinal_identificadores, etiqueta_pai=sinal)

        return