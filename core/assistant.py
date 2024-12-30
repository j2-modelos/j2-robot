import asyncio
import random
from time import sleep
from typing import List
from urllib.parse import urlparse, parse_qs

import websockets
from pycparser.c_ast import Return
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from model.driver_guia import DriverGuia
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
        self.guias_abertas: List[DriverGuia] = []
        self.websocket = None
        self.painel_usuario = None

        self.guias_abertas.append(DriverGuia('guia-principal-aplicacao', self.driver.current_window_handle))

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
            condition_function (function (WebDriver)): Função que define a condição a ser aguardada. Função síncrona.
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
            sleep(0.200)
            return result
        except TimeoutException:
            raise asyncio.TimeoutError("The condition was not met within the specified timeout.")

    async def wait_for_async(self, condition_function, timeout=None):
        """
        Aguarda uma condição personalizada assíncrona ser atendida.

        Args:
            condition_function (function(_driver)): Função assíncrona que define a condição a ser aguardada.
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

    async def wait_for_element_visible(self, locator=None, css_selector=None, timeout=None):
        """
        Aguarda que um elemento se torne visível.

        Args:
            locator (tuple, optional): Tupla (By, value) para localizar o elemento.
            css_selector (str, optional): Um seletor CSS para localizar o elemento.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar.

        Returns:
            WebElement: O elemento encontrado se visível.

        Raises:
            ValueError: Se nenhum locator ou seletor CSS for fornecido.
        """
        # Verificar se locator ou css_selector foi fornecido
        if not locator and not css_selector:
            raise ValueError("Você deve fornecer um 'locator' ou 'css_selector'.")

        # Construir locator com CSS_SELECTOR, se aplicável
        if css_selector:
            locator = (By.CSS_SELECTOR, css_selector)

        # Cria a condição com o locator
        condition = EC.visibility_of_element_located(locator)

        # Definir a condição no wrapper
        def wrapper_condition(driver):
            return condition(driver)

        try:
            await self.wait_for(wrapper_condition, timeout)
        except Exception as e:
            # Propagar ou customizar a exceção de timeout
            raise TimeoutException(f"O elemento com locator {locator} não ficou visível em {timeout} segundos.") from e

        # Após confirmar visibilidade, retorna o elemento
        by, value = locator
        return self.driver.find_element(by, value)

    async def wait_for_element_exist(self, locator=None, css_selector=None, timeout=None):
        """
        Aguarda que um elemento exista no DOM (sem garantir visibilidade).

        Args:
            locator (tuple, optional): Tupla (By, value) para localizar o elemento.
            css_selector (str, optional): Um seletor CSS para localizar o elemento.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar.

        Returns:
            WebElement: O elemento encontrado se presente no DOM.

        Raises:
            ValueError: Se nenhum locator ou seletor CSS for fornecido.
            TimeoutException: Se o elemento não for encontrado em tempo hábil.
        """
        # Verificar se locator ou css_selector foi fornecido
        if not locator and not css_selector:
            raise ValueError("Você deve fornecer um 'locator' ou 'css_selector'.")

        # Construir locator com CSS_SELECTOR, se aplicável
        if css_selector:
            locator = (By.CSS_SELECTOR, css_selector)

        # Criar uma função para verificar a presença do elemento
        def wrapper_condition(driver):
            try:
                # Aqui usamos find_element para verificar a presença no DOM
                element = driver.find_element(*locator)
                return element is not None  # Retorna True se o elemento foi encontrado
            except:
                return False  # Se não encontrar, retorna False

        try:
            # Espera até que o elemento seja encontrado no DOM
            await self.wait_for(wrapper_condition, timeout)
        except Exception as e:
            # Propagar ou customizar a exceção de timeout
            raise TimeoutException(
                f"O elemento com locator {locator} não foi encontrado no DOM em {timeout} segundos.") from e

        # Após confirmar que o elemento existe, retorna o elemento
        by, value = locator
        return self.driver.find_element(by, value)

    def find_element(self, locator=None, css_selector=None,):
        """
        Função alias para o find_element do WebDriver

        Args:
            locator (tuple, optional): Tupla (By, value) para localizar o elemento.
            css_selector (str, optional): Um seletor CSS para localizar o elemento.

        :return: WebElement
        """

        # Verificar se locator ou css_selector foi fornecido
        if not locator and not css_selector:
            raise ValueError("Você deve fornecer um 'locator' ou 'css_selector'.")

        by, value = locator
        return self.driver.find_element(by, value)
        return

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
            sleep(0.100)
            return True
        except asyncio.TimeoutError:
            print("Erro: O Chrome não carregou no tempo esperado.")
            return False

    def clicar_elemento(self, elemento: WebElement = None, locator=None):
        if elemento is None and locator is None:
            raise "Parâmetro elemento ou locator devem ser definidos"

        if not locator is None:
            elemento = self.find_element(locator=locator)

        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(elemento)
            actions.click(elemento)
            actions.perform()
        except :
            print('Erro não interagível ocorreu.')
            self.driver.execute_script("arguments[0].click();", elemento)

    async def wait_for_element_not_more_in_dom(self, element: WebElement, timeout=None):
        """
        Aguarda até que um elemento não esteja mais anexado ao DOM.

        Args:
            element (WebElement): Referência ao elemento a ser monitorado.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar. Padrão: self.timeout.

        Returns:
            bool: True se o elemento não estiver mais no DOM antes do timeout.

        Raises:
            asyncio.TimeoutError: Se o elemento continuar no DOM após o tempo limite.
        """
        timeout = timeout or self.timeout or 86400  # Timeout padrão de 24h, caso não seja especificado

        def element_removed_from_dom(driver):
            return not self.dom_util.is_element_still_in_dom(element)

        try:
            result = await self.wait_for(element_removed_from_dom, timeout)
            return result
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(
                "O elemento ainda está anexado ao DOM após o tempo limite especificado."
            )

    async def wait_abrir_nova_guia(self, url:str, alias:str, timeout=None):
        timeout = timeout or self.timeout or 86400
        print(f"Aguardando abrir: alias: {alias}, url {url}")

        quantidade_guias_atuais = len(self.driver.window_handles)

        self.driver.execute_script(f"window.open('{url}', '_blank')")
        await self.wait_for(lambda d: EC.number_of_windows_to_be( quantidade_guias_atuais+1 ) )
        nova_guia = DriverGuia(alias, self.driver.window_handles[quantidade_guias_atuais])
        self.guias_abertas.append(nova_guia)
        self.driver.switch_to.window(nova_guia.id)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        await self.wait_for_chrome_ready()

        return nova_guia

    async def obter_guia(self, alias=None):
        """
            Obtem e alterna para uma das guias ativas.
        :param alias: alias da guia a alternar. Se None, refere a guia principal da aplicação.
        :return:
        """

        if not alias:
            alias = "guia-principal-aplicacao"

        def encontrar(alias_procurado: str) -> DriverGuia | None:
            for guia_it in self.guias_abertas:
                if guia_it.alias == alias_procurado:
                    return guia_it
            return None

        guia = encontrar(alias)

        if not guia is None:
            self.driver.switch_to.window(guia.id)

        return guia

    async def obter_parametro_url(self, parametro: str):
        current_url = self.driver.execute_script("return window.location.href")
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        param1_value = query_params.get(parametro, [None])[0]
        return str(param1_value)


