from enum import Enum

class EstadoAutomacao(Enum):
    NAO_INICIADA = "EstadoAutomacao.NAO_INICIADA"
    EXECUTANDO = "EstadoAutomacao.EXECUTANDO"
    PAUSADA = "EstadoAutomacao.PAUSADA"
    PARADA = "EstadoAutomacao.PARADA"