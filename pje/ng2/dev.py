import asyncio
from pathlib import Path

from core.web_driver_manager import WebDriverManager
from selenium.webdriver.common.by import By

from frontend.painel_usuario_interno_root import PainelUsuarioInterno


class Dev:
    def __init__(self, drivermgr: WebDriverManager):
        self.drivermgr = drivermgr
        self.ng_frame = None

        asyncio.create_task( self.init_async() )

    async  def init_async(self):
        self.ng_frame = await self.drivermgr.ast().wait_for_element_visible(
            locator=(By.CSS_SELECTOR, '#ngFrame'), timeout=300
        )
        self.drivermgr.assistant.painel_usuario = PainelUsuarioInterno(self.drivermgr, self.ng_frame)

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

            if user_command.tarefa and user_command.tarefa.strip():
                try:
                    await  self.drivermgr.assistant.websocket.send_to_client({
                        'acao': 'estado-lista-de-automacoes',
                        'estado': False
                    })
                    await  self.drivermgr.assistant.painel_usuario.abrir_tarefa(user_command)
                except Exception as e:
                    # Captura qualquer exceção
                    print(f"Ocorreu um erro: {e}")
                finally:
                    await  self.drivermgr.assistant.websocket.send_to_client({
                        'acao': 'estado-lista-de-automacoes',
                        'estado': True
                    })
                    return True



            return True

        flag = True
        while flag:
            flag = await self.drivermgr.assistant.wait_for_async(aguardando_mensagem)

        print('dev.seam: Programa encerrado pelo usuário.')