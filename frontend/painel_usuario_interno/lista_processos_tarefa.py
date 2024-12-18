from core.web_driver_manager import WebDriverManager


class ListaProcessoTarefa:
    def __init__(self, driver: WebDriverManager):
        self.drivermgr = driver
        print("Driver configurado.")