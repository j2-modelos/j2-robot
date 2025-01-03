from typing import List, Tuple

class J2RobotErro(Exception):
    """
    Exceção levantada para erros específicos do domínio j2-robot.

    Esta exceção é usada para identificar e relatar falhas no fluxo de trabalho da
    aplicação, com códigos de erro específicos e mensagens correspondentes.

    Erros conhecidos:

        1. "O frame da tarefa não está mais na ListaProcessosTarefa."
        2. "Erro ocorrido no frame da tarefa."
        3. "Erro durante a transição da tarefa pelo fluxo."
        4. "Erro ao atualizar a lista de processos do painel lista tarefas."
        5. "O frame da tarefa não está saudável para operação"
        6. "Erro de iteração pelos cartões na lista de processos de tarefa."
        7. "Erro durante a espera de resposta do ChatGPT"
        8. "Automação encerrada devido erro em serviço terceiro dependente"

    Exemplo de uso:
        raise J2RobotErro(1)

    A exceção irá carregar a mensagem associada ao código fornecido.
    """

    erros: List[Tuple[int, str]] = [
        (1, "O frame da tarefa não está mais na ListaProcessosTarefa." ),
        (2, "Erro ocorrido no frame da tarefa."),
        (3, "Erro durante a transição da tarefa pelo fluxo."),
        (4, "Erro ao atualizar a lista de processos do painel lista tarefas."),
        (5, "O frame da tarefa não está saudável para operação"),
        (6, "Erro de iteração pelos cartões na lista de processos de tarefa."),
        (7, "Erro durante a espera de resposta do ChatGPT"),
        (8, "Automação encerrada devido erro em serviço terceiro dependente"),
    ]

    def __init__(self, codigo_erro: int, anterior: Exception = None, complemento: str = None):
        self.codigo_erro: int = codigo_erro
        self.mensagem = self._obter_mensagem_erro(codigo_erro)
        self.anterior = anterior
        super().__init__(f"Erro #{codigo_erro:04}: {self.mensagem}{ f' ({complemento})' if complemento else '' }")

    def _obter_mensagem_erro(self, codigo_erro: int) -> str:
        erros = {
            1: "O frame da tarefa não está mais na ListaProcessosTarefa.",
            2: "Erro ocorrido no frame da tarefa.",
            3: "Erro durante a transição da tarefa pelo fluxo."
        }
        return erros.get(codigo_erro, "Erro desconhecido.")