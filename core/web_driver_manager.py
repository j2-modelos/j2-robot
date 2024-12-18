from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
from core.assistant import Assistant

from dotenv import load_dotenv
import os

# Carregar o arquivo .env
load_dotenv()


class WebDriverManager:
    drivers_abertos = []

    def __init__(self, maximize_window=True):
        """
        Inicializa o WebDriverManager.

        :param driver_path: Caminho para o executável do driver, se necessário.
        :param load_extension: Caminho para uma extensão do Chrome a ser carregada.
        :param maximize_window: Se deve maximizar a janela ao abrir o navegador.
        """
        extensao_base_path = str(Path(os.getenv('J2_EXTENSION_PATH')).resolve())
        extensao_versao = os.getenv('J2_EXTENSAO_VERSAO')

        #self.driver_path = os.getenv('CHROME_DRIVER_PATH')
        self.driver_path = str(Path(os.getenv('CHROME_DRIVER_PATH')).resolve())
        self.load_extension = f'{extensao_base_path}/{extensao_versao}'
        self.maximize_window = maximize_window
        self.driver: webdriver = None
        self.assistant: Assistant = None
        self.configure_options()
        self.start_driver()
        WebDriverManager.drivers_abertos.append(self)

    def configure_options(self):
        """
        Configura as opções do Chrome.
        """
        options = Options()

        # Carrega a extensão se fornecido o caminho
        if self.load_extension:
            options.add_argument(f"--load-extension={self.load_extension}")

        # Maximiza a janela se configurado para isso
        if self.maximize_window:
            options.add_argument("--start-maximized")

        return options

    def start_driver(self):
        """
        Inicia o WebDriver do Chrome com as opções configuradas.
        """
        options = self.configure_options()

        if self.driver_path:
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            # Usando o WebDriver gerenciado automaticamente (chromedriver)
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.assistant = Assistant(self.driver)

    def quit_driver(self):
        """
        Fecha o WebDriver.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    def ast(self) -> Assistant:
        return  self.assistant

    def drv(self) -> webdriver:
        """
        retorna o objeto webDrive da instância desse manager
        :return: webdrive
        """
        return  self.driver

    @classmethod
    def close_all_drivers(cls):
        # Fecha todos os drivers abertos e limpa a lista
        for driver in cls.drivers_abertos:
            driver.quit()
        cls.drivers_abertos.clear()

    @classmethod
    def obter_ultimo_driver(cls):
        # Obtém o último driver da lista estática
        if cls.drivers_abertos:  # Verifica se a lista não está vazia
            return cls.drivers_abertos[-1]
        return None  # Caso não haja drivers abertos

