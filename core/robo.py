import time

from core.web_driver_manager import WebDriverManager
from pje.login import  Login
from pje.publico.usuario.token import Token


async def robo():
    try:
        drivermgr = WebDriverManager(maximize_window=True).obter_ultimo_driver()
        estaPronto = await drivermgr.ast().wait_for_chrome_ready()
        if not estaPronto:
            raise ValueError("Google Chrome não ficou pronto.")

        Login(drivermgr).logarUsarioSenha("https://pje.tjma.jus.br/pje/login.seam", username="00641805306", password="a1420f5F5")
        await Token(drivermgr).esperar_insercao_token()

        print("Conseguiu Miserávi")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        # Fechar o navegador
        input("Concluído. Digite qualquer tecla para finalizar")
        WebDriverManager.close_all_drivers()