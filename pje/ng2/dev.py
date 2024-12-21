import asyncio
from pathlib import Path

from core.web_driver_manager import WebDriverManager
from selenium.webdriver.common.by import By


class Dev:
    def __init__(self, driver: WebDriverManager):
        self.drivermgr = driver
        asyncio.create_task( self.init_async() )

    async  def init_async(self):
        await self.drivermgr.ast().wait_for_element_visible(
            locator=(By.CSS_SELECTOR, '#ngFrame'), timeout=300
        )
        with open(str(Path(__file__).parent / "dev_menu_automacao.html"), "r", encoding="utf-8") as file:
            html_injection = file.read()
        with open(str(Path(__file__).parent / "dev_menu_automacao.js"), "r", encoding="utf-8") as file:
            js_injection = file.read()
        self.drivermgr.assistant.dom_util.insert_html(css_selector="#barraSuperiorPrincipal  .navbar-right",
                                                      position="afterbegin",
                                                      html_string=f'{html_injection}')
        self.drivermgr.assistant.dom_util.insert_script(js_injection)



        self._registrar_numero_porta_documento()

        print('Inserido menu do robô')

        return self

    def _registrar_numero_porta_documento(self):
        """
        Atribui a variável J2_ROBO_WEBSOCKET_PORTA no objeto window da página.

        :param porta: Valor que será atribuído à variável J2_ROBO_WEBSOCKET_PORTA.
        """
        porta = self.drivermgr.assistant.ws_port
        script = f"window.J2_ROBO_WEBSOCKET_PORTA = {porta};"
        try:
            # Executando o script no contexto da página
            self.drivermgr.driver.execute_script(script)
            print(f"Variável J2_ROBO_WEBSOCKET_PORTA atribuída ao valor {porta}")
        except Exception as e:
            print(f"Erro ao atribuir a variável J2_ROBO_WEBSOCKET_PORTA: {e}")

    async def esperar_comando_usuario(self):
        print('dev.seam: aguardando pelo comando do usuário')
        async def aguardando_mensagem(driver):
            if self.drivermgr.assistant.websocket is None:
                return True

            user_command = await self.drivermgr.assistant.websocket.ouvir_mensagens()
            if user_command is None:
                print('Uma mensagem invalida foi interpretada')
                return True

            if user_command.acao == 'robo-encerrar-aplicacao':
                return False

            return True

        flag = True
        while flag:
            flag = await self.drivermgr.assistant.wait_for_async(aguardando_mensagem)

        print('dev.seam: Programa encerrado pelo usuário.')