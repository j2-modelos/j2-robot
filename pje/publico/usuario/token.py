from core.web_driver_manager import WebDriverManager
from selenium.webdriver.common.by import By


class Token:
    def __init__(self, driver: WebDriverManager):
        self.driver = driver

    async def esperar_insercao_token(self):
        print(f"Recuperada página do Token PJe")

        await self.driver.ast().wait_for_element_visible(
            locator=(By.XPATH, '//*[@id="tokenAcessoForm"]'), timeout=300
        )

        print(f"Aguardando usuario inserir o Token PJe")