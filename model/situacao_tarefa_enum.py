from enum import Enum

class SituacaoTarefaEnum(Enum):
    ANALISADA = "SituacaoTarefaEnum.ANALISADA"
    ABERTA = "SituacaoTarefaEnum.ABERTA"
    EM_ANALISE = "SituacaoTarefaEnum.EM_ANALISE"
    NAO_RESOLVIDA = "SituacaoTarefaEnum.NAO_RESOLVIDA"
    RESOLVIDA = "SituacaoTarefaEnum.RESOLVIDA"
    FALLBACK = "SituacaoTarefaEnum.FALLBACK"