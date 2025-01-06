import json

import pandas as pd


class GeradorPromptTabelaDecisao:
    rotulo_folha_prompt = "prompt"
    rotulo_fase_avaliacao = "avaliacao"
    #caractere_espaco = " "
    caractere_espaco = "&nbsp;&nbsp;&nbsp;&nbsp;"

    def __init__(self, caminho_tabela=None, json_niveis=1, precisa_transpor=False, cabecalho=None):
        if caminho_tabela is None:
            raise "A tabela de decisão não foi devidamente configurada para operação."

        tabela_folha = pd.read_excel(
            caminho_tabela,
            header=cabecalho)

        prompt_folha = pd.read_excel(
            caminho_tabela,
            header=cabecalho, sheet_name="prompt")


        print("GeradorPromptTabelaDecisao: tabela_folha:", tabela_folha)
        print("GeradorPromptTabelaDecisao: prompt_folha:", prompt_folha)

        self.promp_folha = prompt_folha

        if not precisa_transpor:
            tabela_folha = tabela_folha.T
            print("GeradorPromptTabelaDecisao: tabela_folha transposta:", tabela_folha)

        self.tabela_configuracao = tabela_folha.iloc[:, :(json_niveis + 2)]
        self.indice_tipo_dado_json_prompt = json_niveis + 1

        print("GeradorPromptTabelaDecisao: cabeçalho tabela_folha decisão:")
        print(self.tabela_configuracao)

        del tabela_folha

    def preparar_html_fragament_json_definicao(self, json_para_analise):
        try:
            # Iterar pelas linhas do corpo
            linhas_fragment_html = []
            linhas_fragment_html.append("<p>")
            linhas_fragment_html.append("    <br>{")

            level_json = 0
            linha_anterior = []
            for linha in self.tabela_configuracao.values:
                if linha[0] != GeradorPromptTabelaDecisao.rotulo_fase_avaliacao:
                    continue

                tipo = linha[self.indice_tipo_dado_json_prompt] or "[NÃO DEFINIDO]"
                tipo = tipo.strip('"')
                propriedade_chave = None
                linha_iterar = linha[1:-1]
                linha_len = len(linha_iterar)

                #print("PARCIAL:")
                #print("\n".join(linhas_fragment_html))

                for indice, chave in enumerate(linha_iterar):
                    if len(linha_anterior) != 0 and (linha_iterar[indice] == linha_anterior[indice]):
                        continue

                    if len(linha_anterior) != 0 and linha_iterar[indice] != linha_anterior[indice]:
                       while level_json != indice:
                            linha_fragment = f'    <br>{GeradorPromptTabelaDecisao.caractere_espaco * 2 * level_json}}}'
                            linhas_fragment_html.append(linha_fragment)
                            level_json -= 1
                            #print("PARCIAL:")
                            #print("\n".join(linhas_fragment_html))

                    if not pd.isna(chave):  # Verifica se o valor não é NaN
                        propriedade_chave = chave
                    if indice < linha_len-1 and not pd.isna(linha_iterar[indice+1]):
                        level_json += 1
                        linha_fragment = f'    <br>{GeradorPromptTabelaDecisao.caractere_espaco * 2 * (indice + 1)}{propriedade_chave}: {{'
                        linhas_fragment_html.append(linha_fragment)
                        #print("PARCIAL:")
                        #print("\n".join(linhas_fragment_html))
                    else:
                        linha_fragment = f'    <br>{GeradorPromptTabelaDecisao.caractere_espaco * 2 * (indice + 1)}{propriedade_chave}: "{tipo}",'
                        linhas_fragment_html.append(linha_fragment)
                        #print("PARCIAL:")
                        #print("\n".join(linhas_fragment_html))
                        break

                linha_anterior = linha_iterar

                if propriedade_chave is None:
                    raise Exception("Propriedade chave não pode ser None")

            linhas_fragment_html.append("    <br>}")
            linhas_fragment_html.append("</p>")
            print("FINAL")
            print("\n".join(linhas_fragment_html))

        except Exception as e:
            print("Deu erro")

    @staticmethod
    def _normalizar_valor_celula(valor):
        if (pd.isna(valor)):
            return valor

        if isinstance(valor, str):
            valor = valor.lower()
            if valor == 'true' or valor == 'sim':
                valor = True
            elif valor == 'false' or valor == 'nao' or valor == "não":
                valor = False

        return valor

    def preparar_fragmento_orientacoes_chave(self):
        try:
            # Iterar pelas linhas do corpo
            linhas_fragment_html = []

            for linha in self.promp_folha.values:
                propriedade_chave, orientacao = linha
                compilado = orientacao.replace("$chave_prompt", propriedade_chave)
                linhas_fragment_html.append(compilado)

            resultado = "".join(f"<p>\n    {elemento}\n</p>\n" for elemento in linhas_fragment_html)
            return resultado

        except Exception as e:
            print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    # Ler o arquivo Excel. Substitua 'arquivo.xlsx' pelo caminho do seu arquivo Excel.
    depuracao = False
    if not depuracao:
        caminho_tabela = 'C:/Dev/j2-robot/fluxo/tarefas/avaliar_determinacoes_do_magistrado/avaliar_determinacoes_do_magistrado_tabela_decisao.xlsx'
    else:
        caminho_tabela = 'C:/Dev/j2-robot/fluxo/tarefas/avaliar_determinacoes_do_magistrado/avaliar_determinacoes_do_magistrado_tabela_decisao_depuracao.xlsx'
    resolutor = GeradorPromptTabelaDecisao(caminho_tabela=caminho_tabela, json_niveis=3, precisa_transpor=True)

    analise_json = json.loads(
        """
{
        o_tipo_do_ato_judicial_eh: "sentenca" ou "despacho" ou "decisao",
        se_for_despacho: {
                determina_inicio_da_fase_de_execucao_judidcial: "true ou false",
                determina_que_uma_audiencia_de_conciliacao_deve_ser_realizada_no_processo: "true ou false",
                determina_que_a_parte_comprove_o_seu_interesse_de_agir_mediante_tentativa_de_solucao_anterior: "true ou false",
                se_determina_a_emenda_da_peticao_inicial_no_prazo_15_dias: {
                        sim_determina: "true ou false",
                        determina_retornar_autos_para_decisao_urgencia_ou_decisao_liminar: "true ou false",
                }
        }
        se_for_sentenca: {
                julgamento_com_merito: "true ou false",
                julgamento_sem_merito: "true ou false",
                ha_uma_obrigacao_de_fazer_a_ser_cumprida: {
                        sim_ha: "true ou false",
                        a_obrigacao_de_fazer_esta_no_mesmo_paragrafo_que_ha_confirmacao_de_liminar: "true ou false",
                }
                eh_uma_homolocao_de_acordo: "true ou false",
                determina_se_deve_ser_expedido_algum_oficio_judicial_a_uma_outra_autoridade: "true ou false",
        }
        se_for_decisao: {
                decisao_recebeu_um_recurso_com_ou_sem_efeito_suspensivo: "true ou false",
                decisao_diz_respeito_concessao_ou_nao_de_uma_tutela_provisoria: "true ou false",
                decisao_diz_respeito_a_embargos_de_declaracao: "true ou false",
        }
        determina_apenas_a_intimacao_de_partes_no_processo: "true ou false",
        existe_determinacao_para_incluir_ou_retirar_partes_do_processo: "true ou false",
        existe_determinacao_para_arquivar_o_processo: "true ou false",
        a_classe_do_processo_eh: "uma string em lower case",
        houve_decretacao_revelia: "true ou false",
}
        """
    )

    try:
        resolutor.preparar_html_fragament_json_definicao(analise_json)
        print(resolutor.preparar_fragmento_orientacoes_chave())
    except Exception as e:
        print(e)