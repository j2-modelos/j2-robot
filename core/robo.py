import asyncio
import os
import threading
import time

import psutil

from core.web_driver_manager import WebDriverManager
from pje.login import  Login
from pje.ng2.dev import Dev
from pje.publico.usuario.token import Token
from utils.env import ENV_LOGIN_URL, ENV_LOGIN_USUARIO, ENV_LOGIN_SENHA


async def robo():
    try:
        drivermgr = WebDriverManager(maximize_window=True).obter_ultimo_driver()
        estaPronto = await drivermgr.ast().wait_for_chrome_ready()
        if not estaPronto:
            raise ValueError("Google Chrome não ficou pronto.")

        Login(drivermgr).logarUsarioSenha(ENV_LOGIN_URL, username=ENV_LOGIN_USUARIO, password=ENV_LOGIN_SENHA)
        await Token(drivermgr).esperar_insercao_token()
        await Dev(drivermgr).esperar_comando_usuario()

        print("Encerramento do robÔ.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        # Fechar o navegador
        WebDriverManager.close_all_drivers()
        print("A aplicação foi encerrada.")


def iniciar_robo():
    # Verifica se já existe um processo com o nome deste script
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'python' in proc.info['name'] and os.path.basename(__file__) in proc.info['cmdline']:
            print("O robô já está em execução! (Processo existente)")
            return

    # Função que roda um loop de eventos assíncrono dentro da thread
    def run_robo():
        asyncio.run( robo() )  # Essa linha chama o robô na nova thread, permitindo o comportamento assíncrono.

    # Criação da thread
    thread = threading.Thread(target=run_robo)
    thread.start()
    print("Thread do robô iniciada!")