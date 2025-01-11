from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
from core.assistant import Assistant

from dotenv import load_dotenv
import os

from model.driver_guia import DriverGuia
from utils.env import ENV_J2_EXTENSION_PATH, ENV_J2_EXTENSAO_VERSAO, ENV_CHROME_DRIVER_PATH, ENV_CHROME_USER_DATA_DIR, \
    ENV_PERFIL_CHROME, ENV_DOWNLOAD_FOLDER
from utils.path import get_resource_path


class WebDriverManager:
    drivers_abertos = []

    def __init__(self, maximize_window=True):
        """
        Inicializa o WebDriverManager.

        :param driver_path: Caminho para o executável do _driver, se necessário.
        :param load_extension: Caminho para uma extensão do Chrome a ser carregada.
        :param maximize_window: Se deve maximizar a janela ao abrir o navegador.
        """
        extensao_base_path = get_resource_path(ENV_J2_EXTENSION_PATH, packaged=False)
        extensao_versao = ENV_J2_EXTENSAO_VERSAO

        #self.driver_path = os.getenv('CHROME_DRIVER_PATH')
        self.driver_path =  get_resource_path(ENV_CHROME_DRIVER_PATH, packaged=False)
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

        download_folder_path = get_resource_path(ENV_DOWNLOAD_FOLDER, packaged=False)

        options.add_experimental_option('prefs', {
            "download.default_directory": download_folder_path,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "download.open_pdf_in_system_reader": False,
            "profile.default_content_settings.popups": 0
        })

        # Configurar opções do Chrome
        user_data_dir = get_resource_path(ENV_CHROME_USER_DATA_DIR, packaged=False)
        perfil_chrome = ENV_PERFIL_CHROME
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument(
            f'--profile-directory={ perfil_chrome }')  # Geralmente é 'Default', a menos que você tenha múltiplos perfis
        #options.add_argument("--disable-extensions")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')

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

        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
            driver.quit_driver()
        cls.drivers_abertos.clear()

    @classmethod
    def obter_ultimo_driver(cls):
        # Obtém o último _driver da lista estática
        if cls.drivers_abertos:  # Verifica se a lista não está vazia
            return cls.drivers_abertos[-1]
        return None  # Caso não haja drivers abertos

