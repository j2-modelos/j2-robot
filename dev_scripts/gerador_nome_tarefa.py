import random
import string


def gerar_acao_judicial():
    # List of action initials
    acoes = ["ARI", "ARE", "AIE", "AJE", "AVD", "ADM", "APE", "ACC", "ACL", "ATR"]

    # Escolhendo aleatoriamente uma ação
    acao = random.choice(acoes)

    # Gerando um número aleatório no formato "0809874-56.2021.8.11.0037"
    numero = f"080{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.2025.8.10.{random.randint(1000, 9999)}"

    return f"{acao} {numero}"


# Código para execução quando o script for rodado diretamente
if __name__ == "__main__":
    # Repetindo o print 10 vezes
    for _ in range(10):
        print(gerar_acao_judicial())
