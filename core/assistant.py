import asyncio
import random
import websockets

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils.dom import Dom
from utils.websocket_server_client import WebSocketServerClient


class Assistant:
    def __init__(self, driver, timeout=None):
        """
        Inicializa a classe Assistant com um WebDriver e o timeout padrão.
        """
        self.driver = driver
        self.timeout = timeout
        self.dom_util = Dom(driver)
        self.ws_port = random.randint(49152, 65535)
        self.websocket = None

        asyncio.create_task(self._init_async())

    async def _init_async(self):
        """
        Inicialização assíncrona do Assistant:
            1 - Conecta o Assistant a um WebSocket usando a porta gerada aleatoriamente.

        Returns:
            None: Várias inicializações.
        """
        try:
            await self._create_websocket_server()

        except Exception as e:
            print(f"Erro ao conectar ao WebSocket: {e}")

    async def _create_websocket_server(self):
        self.websocket = WebSocketServerClient(host='localhost', port=self.ws_port)
        self.websocket.start()
        print(f"Conectado ao WebSocket na porta {self.ws_port}")


    async def wait_for(self, condition_function, timeout=None):
        """
        Aguarda uma condição personalizada ser atendida de forma assíncrona.

        Args:
            condition_function (function): Função que define a condição a ser aguardada.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar a condição. Padrão: self.timeout.

        Returns:
            O resultado da condição se atendida.
        Raises:
            asyncio.TimeoutError: Se a condição não for atendida dentro do tempo limite.
        """
        timeout = timeout or self.timeout or 86400

        # Wrap the condition_function to work with asyncio
        def wrapper_condition(self_driver):
            try:
                return condition_function(self_driver)
            except Exception:
                return False

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: WebDriverWait(self.driver, timeout).until(wrapper_condition)
            )
            return result
        except TimeoutException:
            raise asyncio.TimeoutError("The condition was not met within the specified timeout.")

    async def wait_for_async(self, condition_function, timeout=None):
        """
        Aguarda uma condição personalizada assíncrona ser atendida.

        Args:
            condition_function (function): Função assíncrona que define a condição a ser aguardada.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar a condição. Padrão: self.timeout.

        Returns:
            O resultado da condição se atendida.
        Raises:
            asyncio.TimeoutError: Se a condição não for atendida dentro do tempo limite.
        """
        timeout = timeout or self.timeout

        # Executando a condição em um loop de eventos, pois a condição é assíncrona
        async def wrapper_condition(self_driver):
            try:
                # Espera o resultado assíncrono da condição
                return await condition_function(self_driver)
            except Exception:
                return False

        loop = asyncio.get_event_loop()
        try:
            # Use `asyncio.wait_for` para lidar com o timeout e aguardar a condição
            result = await asyncio.wait_for(wrapper_condition(self.driver), timeout)
            return result
        except TimeoutException:
            raise asyncio.TimeoutError("A condição não foi atendida dentro do tempo especificado.")

    async def wait_for_element_visible(self, locator, timeout=None):
        """
        Aguarda que um elemento se torne visível.

        Args:
            locator (tuple): Tupla (By, value) para localizar o elemento.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar.

        Returns:
            WebElement: O elemento encontrado se visível.
        """
        # Cria a condição com o locator
        condition = EC.visibility_of_element_located(locator)

        # Definindo o lambda separadamente
        def wrapper_condition(driver):
            return condition(driver)

        return await self.wait_for(wrapper_condition, timeout)

    async def wait_for_manual_input(self, input_locator, timeout=None):
        """
        Aguarda intervenção manual do usuário para preencher um campo de input.

        Args:
            input_locator (tuple): Tupla (By, value) para localizar o campo de input.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar.

        Returns:
            str: O valor final do campo input.
        """
        timeout = timeout or self.timeout

        async def user_input_provided(driver):
            element = driver.find_element(*input_locator)
            value = element.get_attribute("value")
            return value if value.strip() else False

        result = await self.wait_for(user_input_provided, timeout)
        return result

    async def wait_for_chrome_ready(self, timeout=None):
        """
        Aguarda o navegador Chrome carregar completamente.

        Args:
            timeout (int, optional): Tempo máximo (em segundos) para aguardar.
                                     Padrão: self.timeout.

        Returns:
            bool: Verdadeiro se o Chrome está pronto.
        """
        timeout = timeout or self.timeout  # Usa o timeout fornecido ou o padrão

        try:
            print("Aguardando o Chrome estar pronto...")
            # Verificar o estado da página até que esteja "complete"
            await self.wait_for(
                lambda driver: driver.execute_script("return document.readyState") == "complete",
                timeout=timeout
            )
            print("O Chrome está pronto!")
            return True
        except asyncio.TimeoutError:
            print("Erro: O Chrome não carregou no tempo esperado.")
            return False