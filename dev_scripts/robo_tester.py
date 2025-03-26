import asyncio
from time import sleep

from ia.chatgpt import ChatGpt
from ia.claude import Claude
from core.web_driver_manager import WebDriverManager
from dev_scripts.gerador_nome_tarefa import gerar_acao_judicial


async def robo():
    try:
        drivermgr = WebDriverManager(maximize_window=True).obter_ultimo_driver()
        estaPronto = await drivermgr.ast().wait_for_chrome_ready()
        if not estaPronto:
            raise ValueError("Google Chrome não ficou pronto.")

        sleep(2)
        # ia = ChatGpt(drivermgr=drivermgr, guia_compartilhada=True)
        ia = Claude(drivermgr=drivermgr, guia_compartilhada=True)
        await  ia.init_async()

        while True:
            titulo_chat = gerar_acao_judicial()
            await ia.iniciar_novo_chat(titulo_chat)

            resposta = input("Digite 'sim' para sair do loop: ")
            if resposta.lower() == "sim":  # Garante que 'sim' seja insensível a maiúsculas/minúsculas
                print("Saindo do loop...")
                break
            sleep(0.200)

        print("Encerramento do robÔ.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        # Fechar o navegador
        WebDriverManager.close_all_drivers()
        print("A aplicação foi encerrada.")


if __name__ == "__main__":
    asyncio.run( robo() )