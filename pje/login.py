from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from core.web_driver_manager import WebDriverManager


class Login:
    def __init__(self, driver: WebDriverManager):
        self.drivermgr = driver
        print("Driver configurado.")

    def logarUsarioSenha(self, url, username, password):
        """Método para realizar o login usando o driver configurado"""
        if not self.drivermgr:
            print("Erro: Nenhum driver configurado.")
            return
        try:
            # Exemplo de login em uma página
            self.drivermgr.driver.get(url)  # Navega até a URL
            self.drivermgr.driver.switch_to.frame(0)
            self.drivermgr.driver.find_element(By.ID, "username").send_keys(username)  # Insere o usuário
            self.drivermgr.driver.find_element(By.ID, "password").send_keys(password)  # Insere a senha
            self.drivermgr.driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            print("Login realizado com sucesso.")
        except Exception as e:
            print(f"Erro ao tentar logar: {e}")

        sleep(10)
        input("Pressione Enter para encerrar os navegadores...")