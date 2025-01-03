import json

import pandas as pd

class ResolutorTabelaDecisao:
    rotulo_controle_encerramento_loop_avaliacao = "encerra_decisao"
    rotulo_marcador_identificacao = "identificacao"
    rotulo_fase_avaliacao = "avaliacao"
    rotulo_fase_acao = "acao"
    rotulo_fase_controle = "controle"
    rotulo_fallback = "fallback"
    rotulo_fallback_identificador = "FALB"

    def __init__(self, caminho_tabela=None, tabela=None, json_niveis=1, precisa_transpor=False, cabecalho=None):
        if caminho_tabela is None and tabela is None:
            raise "A tabela de decisão não foi devidamente configurada para operação."
        if caminho_tabela:
            tabela = pd.read_excel(
                caminho_tabela,
                header=cabecalho)
        print("ResolutorTabelaDecisao: tabela:", tabela)

        if precisa_transpor:
            tabela = tabela.T
            print("ResolutorTabelaDecisao: tabela transposta:", tabela)

        self.tabela_cabecalho = tabela.iloc[:(json_niveis+1), :]
        self.tabela_corpo = tabela.iloc[(json_niveis+1):, :]

        print("ResolutorTabelaDecisao: cabeçalho tabela decisão:")
        print(self.tabela_cabecalho)
        print("ResolutorTabelaDecisao: corpo tabela decisão:")
        print(self.tabela_corpo)

        del tabela

        self.identificadores = None
        self.medida_a_tomar = None
        self.estado_resolucao = None
        self.mensagem_erro = None

    def decidir(self, json_para_analise):
        try:
            # Iterar pelas linhas do corpo
            medidas_a_tomar = []
            identificadores_decisao = []
            medida_encerramento_encontrada = False

            for linha_corpo in self.tabela_corpo.values:
                print("Processando linha do corpo:")

                fase = None
                decidido_executar_acao = True
                analise_json_reconstrucao = None
                eh_fallback = False
                identificacao_decisao = None

                # Iterar pelas colunas do cabeçalho
                for i, coluna_cabeçalho in enumerate(self.tabela_cabecalho.columns):
                    if pd.isna(linha_corpo[i]):
                        continue

                    valores_cabecalhos = []
                    # Pegar o valor correspondente da linha do corpo e da coluna
                    corpo_celula_valor = ResolutorTabelaDecisao._normalizar_valor_celula(linha_corpo[i])
                    corpo_celula_valor_original = linha_corpo[i]
                    deve_continuar_proxima_avaliacao = False
                    for j, linhas_cabeçalho in enumerate(self.tabela_cabecalho.values):
                        valores_cabecalhos.append(str(self.tabela_cabecalho.iloc[
                                                          j, i]))

                        cabecalho_celula_valor =  self.tabela_cabecalho.iloc[j, i]
                        if cabecalho_celula_valor == ResolutorTabelaDecisao.rotulo_marcador_identificacao:
                            identificacao_decisao = corpo_celula_valor
                            break
                        elif (cabecalho_celula_valor == ResolutorTabelaDecisao.rotulo_fase_avaliacao
                              or cabecalho_celula_valor == ResolutorTabelaDecisao.rotulo_fase_acao
                              or cabecalho_celula_valor == ResolutorTabelaDecisao.rotulo_fase_controle):
                            fase = cabecalho_celula_valor
                        else:
                            if fase == ResolutorTabelaDecisao.rotulo_fase_avaliacao:
                                if pd.isna(cabecalho_celula_valor):
                                    continue
                                if corpo_celula_valor == ResolutorTabelaDecisao.rotulo_fallback:
                                    identificacao_decisao = ResolutorTabelaDecisao.rotulo_fallback_identificador
                                    eh_fallback = True
                                    continue
                                elif analise_json_reconstrucao is None:
                                    if cabecalho_celula_valor in json_para_analise and not json_para_analise[cabecalho_celula_valor] is None:
                                        analise_json_reconstrucao = json_para_analise[cabecalho_celula_valor]
                                else:
                                    if cabecalho_celula_valor in analise_json_reconstrucao and not analise_json_reconstrucao[cabecalho_celula_valor] is None:
                                        analise_json_reconstrucao = analise_json_reconstrucao[cabecalho_celula_valor]

                            elif fase == ResolutorTabelaDecisao.rotulo_fase_acao:
                                if decidido_executar_acao or eh_fallback:
                                    if not pd.isna(cabecalho_celula_valor):
                                        print(f"{"=>" * 50 }Ação será tomada: {cabecalho_celula_valor}: {corpo_celula_valor}")


                                        for acao in medidas_a_tomar:
                                            if cabecalho_celula_valor in acao:
                                                acao[cabecalho_celula_valor].append( corpo_celula_valor_original )
                                                break
                                        else:
                                            nova_acao = {cabecalho_celula_valor: [corpo_celula_valor_original]}
                                            medidas_a_tomar.append(nova_acao)

                                        if (decidido_executar_acao or eh_fallback) and not identificacao_decisao.upper() in identificadores_decisao:
                                            identificadores_decisao.append(identificacao_decisao.upper())

                                else:
                                    deve_continuar_proxima_avaliacao = True
                                    break
                            elif fase == ResolutorTabelaDecisao.rotulo_fase_controle:
                                if ( decidido_executar_acao
                                and cabecalho_celula_valor == ResolutorTabelaDecisao.rotulo_controle_encerramento_loop_avaliacao
                                and corpo_celula_valor == True):
                                    medida_encerramento_encontrada = True
                                    print(
                                        f"{"=>" * 50}Controle realizado: {cabecalho_celula_valor}: {corpo_celula_valor}")
                            else:
                                raise "Condição não esperada ocorrida"

                    if fase == ResolutorTabelaDecisao.rotulo_fase_avaliacao:
                        if deve_continuar_proxima_avaliacao:
                            analise_json_reconstrucao = None
                            continue

                        if isinstance(corpo_celula_valor, str):
                            valores_criterio_avaliacao = corpo_celula_valor.split(";") if isinstance(corpo_celula_valor, str) else corpo_celula_valor
                            decidido_executar_acao = decidido_executar_acao and (analise_json_reconstrucao in valores_criterio_avaliacao)
                        else:
                            decidido_executar_acao = decidido_executar_acao and analise_json_reconstrucao == corpo_celula_valor

                        analise_json_reconstrucao = None

                    # Exibir os valores
                    print(f"Fase: {fase} | Corpo: {corpo_celula_valor} | Cabeçalho: { " + ".join(valores_cabecalhos)}")

                print("-" * 30)
                if medida_encerramento_encontrada:
                    print("Iteração encerrada mediante medida de encerramento encontrada.")
                    break

            print("Resultados da decisão:")
            print("Identificadores: ", identificadores_decisao)
            print("Medidas a tomar: ", medidas_a_tomar)

            self.identificadores = identificadores_decisao
            self.medida_a_tomar = medidas_a_tomar
            self.estado_resolucao = "sucesso"
            self.mensagem_erro = None
        except Exception as e:
            self.identificadores = [ "erro" ]
            self.medida_a_tomar = {}
            self.estado_resolucao = "erro"
            self.mensagem_erro = e
        return

    @staticmethod
    def _normalizar_valor_celula(valor):
        if (pd.isna(valor)):
            return valor

        if isinstance(valor, str):
            valor = valor.lower()
            if valor == 'true' or valor == 'sim' :
                valor = True
            elif valor == 'false' or valor == 'nao' or valor == "não":
                valor = False

        return valor

if __name__ == "__main__":
    #Ler o arquivo Excel. Substitua 'arquivo.xlsx' pelo caminho do seu arquivo Excel.
    depuracao = False
    if not depuracao:
        caminho_tabela = 'C:/Dev/j2-robot/fluxo/tarefas/avaliar_determinacoes_do_magistrado/avaliar_determinacoes_do_magistrado_tabela_decisao.xlsx'
    else:
        caminho_tabela = 'C:/Dev/j2-robot/fluxo/tarefas/avaliar_determinacoes_do_magistrado/avaliar_determinacoes_do_magistrado_tabela_decisao_depuracao.xlsx'
    resolutor = ResolutorTabelaDecisao(caminho_tabela=caminho_tabela, json_niveis=3, precisa_transpor=True)



    analise_json = json.loads(
        """
        
{
  "json_uuid": "$uuid",
  "ato_judicial_uuid": "$ato_uuid",
  "o_tipo_do_ato_judicial_eh": "sentenca",
  "se_for_sentenca": {
    "julgamento_com_merito": true,
    "julgamento_sem_merito": false,
    "ha_uma_obrigacao_de_fazer_a_ser_cumprida": {
      "sim_ha": true,
      "a_obrigacao_de_fazer_esta_no_mesmo_paragrafo_que_ha_confirmacao_de_liminar": false
    },
    "eh_uma_homolocao_de_acordo": false,
    "determina_se_deve_ser_expedido_algum_oficio_judicial_a_uma_outra_autoridade": false
  },
  "se_for_despacho": {},
  "se_for_decisao": {},
  "determina_apenas_a_intimacao_de_partes_no_processo": true,
  "existe_determinacao_para_incluir_ou_retirar_partes_do_processo": false,
  "existe_determinacao_para_arquivar_o_processo": true,
  "a_classe_do_processo_eh": "procedimento do juizado especial civel",
  "houve_decretacao_revelia": false
}

        
        """
    )

    try:
        resolutor.decidir(analise_json)
    except Exception as e:
        print(e)