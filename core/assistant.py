import asyncio
import random
from time import sleep
from typing import Any, List, Tuple, Awaitable, Union
from urllib.parse import urlparse, parse_qs

import websockets
from pycparser.c_ast import Return
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from model.driver_guia import DriverGuia
from model.estado_automacao_enum import EstadoAutomacao
from model.j2_robot_erro import J2RobotErro
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
        self.action = ActionChains(driver)
        self.estado_automacao = EstadoAutomacao.NAO_INICIADA

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


    async def wait_for_and_state_controller(self, condition_function, timeout=None, avoid_recursion=False):
        """
        Aguarda uma condição personalizada ser atendida de forma assíncrona.
        Méto-do também realiza o controle do estado de execução da automação da aplicaçao.
        Args:
            condition_function (function (WebDriver)): Função que define a condição a ser aguardada. Função síncrona.
            timeout (int, optional): Tempo máximo (em segundos) para aguardar a condição. Padrão: self.timeout.

        Returns:
            O resultado da condição se atendida.
        Raises:
            asyncio.TimeoutError: Se a condição não for atendida dentro do tempo limite.
            :param avoid_recursion: quando do controle de estado, realizada o cuidado de evitar a recursão na execuçáo
        """
        timeout = timeout or self.timeout or 86400

        # Wrap the condition_function to work with asyncio
        def wrapper_condition(self_driver):
            try:
                if not avoid_recursion and self.estado_automacao != EstadoAutomacao.NAO_INICIADA and self.estado_automacao != EstadoAutomacao.EXECUTANDO:
                    raise J2RobotErro(9, complemento=f"Assistant.wait_for->{self.estado_automacao}")

                return condition_function(self_driver)

            except J2RobotErro as e:
                raise e
            except Exception:
                return False

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: WebDriverWait(self.driver, timeout).until(wrapper_condition)
            )
            await asyncio.sleep(0.200)
            return result

        except J2RobotErro as e:
            if e.complemento.endswith(str(EstadoAutomacao.PAUSADA)):
                await self.wait_for_and_state_controller(lambda d: self.estado_automacao != EstadoAutomacao.PAUSADA, avoid_recursion=True)
                if self.estado_automacao == EstadoAutomacao.PARADA:
                    raise J2RobotErro(9, complemento=f"Assistant.wait_for->{self.estado_automacao}")
                elif self.estado_automacao == EstadoAutomacao.EXECUTANDO:
                    return await self.wait_for_and_state_controller(condition_function, timeout, avoid_recursion=False)
                else:
                    raise J2RobotErro(codigo_erro=10)
            elif e.complemento.endswith(str(EstadoAutomacao.PARADA)):
                raise e

        except TimeoutException:
            raise asyncio.TimeoutError("The condition was not met within the specified timeout.")

    async def wait_for_async(self, condition_function, timeout=None, admissible_exceptions=None):
        """
        Aguarda uma condição personalizada assíncrona ser atendida.

        Args:
            async condition_function (function(_driver)): Função assíncrona que define a condição a ser aguardada.
            timeout (float, optional): Tempo máximo (em segundos) para aguardar a condição. Padrão: self.timeout.
            admissible_exceptions (tuple, optional): Exceções que são esperadas e devem ser tratadas como falha normal da condição.

        Returns:
            True, como resultado da condição quando atendida.
        Raises:
            asyncio.TimeoutError: Se a condição não for atendida dentro do tempo limite.
        """
        timeout = timeout or self.timeout or float('inf')
        if admissible_exceptions is None:
            admissible_exceptions = ()  # Define como uma tupla vazia se não especificado
        start_time = asyncio.get_event_loop().time()

        async def wrapper_condition(self_driver):
            try:
                # Espera o resultado assíncrono da condição
                return await condition_function(self_driver)
            except admissible_exceptions:  # Captura apenas as exceções admissíveis
                return False
            except Exception as e:
                raise e  # Relança outras exceções

        while True:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            remaining_time = timeout - elapsed_time

            # Se o tempo já passou, levantamos o erro de timeout
            if remaining_time <= 0:
                raise asyncio.TimeoutError("A condição não foi atendida dentro do tempo especificado.")

            # Espera pela condição com o tempo restante
            try:
                result = await asyncio.wait_for(wrapper_condition(self.driver), remaining_time)
                if result:  # Se a condição for atendida
                    return True
            except asyncio.TimeoutError:
                raise asyncio.TimeoutError("A condição não foi atendida dentro do tempo especificado.")
            except Exception as e:
                # Opcional: log de exceção ou re-encaminhamento
                raise e

            # Aguarda um pequeno intervalo antes de tentar novamente, caso necessário
            await asyncio.sleep(0.1)

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
            await self.wait_for_and_state_controller(wrapper_condition, timeout)
        except J2RobotErro as e:
            raise e
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
            await self.wait_for_and_state_controller(wrapper_condition, timeout)
        except J2RobotErro as e:
            raise e
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
        if css_selector:
            locator=(By.CSS_SELECTOR, css_selector)

        by, value = locator
        return self.driver.find_element(by, value)

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

        result = await self.wait_for_and_state_controller(user_input_provided, timeout)
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
            await self.wait_for_and_state_controller(
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
            actions = self.action
            actions.move_to_element(elemento)
            actions.click(elemento)
            actions.perform()
        except :
            print('Erro não interagível ocorreu.')
            self.driver.execute_script("arguments[0].click();", elemento)

    def scroll_intoview(self, elemento: WebElement):
        self.driver.execute_script("""
            arguments[0].scrollIntoView({
                behavior: 'smooth', 
                block: 'nearest'
            });
        """, elemento)

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
        timeout = timeout or self.timeout or float("inf")  # Timeout padrão de 24h, caso não seja especificado

        def element_removed_from_dom(driver):
            return not self.dom_util.is_element_still_in_dom(element)

        try:
            result = await self.wait_for_and_state_controller(element_removed_from_dom, timeout)
            return result
        except J2RobotErro as e:
            raise e
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(
                "O elemento ainda está anexado ao DOM após o tempo limite especificado."
            )

    async def wait_abrir_nova_guia(self, url:str, alias:str, timeout=None):
        timeout = timeout or self.timeout or 86400
        print(f"Aguardando abrir: alias: {alias}, url {url}")

        quantidade_guias_atuais = len(self.driver.window_handles)

        self.driver.execute_script(f"window.open('{url}', '_blank')")
        await self.wait_for_and_state_controller(lambda d: EC.number_of_windows_to_be(quantidade_guias_atuais + 1))
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

    async def obter_url_frame_ativo(self):
        current_url = self.driver.execute_script("return window.location.href")
        return current_url

    async def wait_race(
            self,
            tasks: List[Union[Awaitable[Any], Tuple[Awaitable[Any], Any]]],
            timeout=None
    ) -> Tuple[Any, Awaitable[Any], Any]:
        """
        Espera pela primeira tarefa a ser concluída entre várias fornecidas.

        Args:
            tasks (List[Union[Awaitable[Any], Tuple[Awaitable[Any], Any]]]):
                Uma lista de corrotinas/tarefas assíncronas ou tuplas (corrotina, valor adicional).
            timeout (float, optional): Tempo limite para aguardar a conclusão.

        Returns:
            Tuple[Any, Awaitable[Any], Any]:
                O resultado da primeira tarefa concluída, a própria tarefa correspondente,
                e o valor adicional associado (ou None se não for uma tupla).
        """
        timeout = timeout or self.timeout or float("inf")

        # Preparar a lista de tarefas no formato padrão (future, extra_value)
        prepared_tasks = [
            (asyncio.create_task(task) if isinstance(task, Awaitable) else asyncio.create_task(task[0]), task[1] if isinstance(task, tuple) else None)
            for task in tasks
        ]

        # Mapear as tarefas para asyncio
        tasks_to_wait = [pair[0] for pair in prepared_tasks]

        # Espera pelas tarefas
        done, pending = await asyncio.wait(tasks_to_wait, return_when=asyncio.FIRST_COMPLETED, timeout=timeout)

        # Cancela as tarefas pendentes
        for task in pending:
            task.cancel()

        # Selecionar a primeira completada
        first_done = next(iter(done))
        result = first_done.result()

        # Associar valor extra, se houver
        extra_value = None
        for future, value in prepared_tasks:
            if future == first_done:
                extra_value = value
                break

        return result, first_done, extra_value

    def campo_limpar_e_escrever(self, campo: WebElement, texto_escrever: str):
        (self.action
         .move_to_element(campo)
         .key_down(Keys.SHIFT).send_keys(Keys.HOME).key_up(Keys.SHIFT)
         .send_keys(Keys.DELETE)
         .send_keys(texto_escrever)
         .send_keys(Keys.RETURN)
         .perform()
         )

    async def verificar_modificacao_status_automacao(self):
        """
        Verifica o estado atual da automação e decide se deve prosseguir, aguardar ou encerrar.

        Esta função analisa o atributo `estado_automacao` da instância da classe (provavelmente
        um valor enumerado do tipo `EstadoAutomacao`) e executa ações com base em três possíveis
        estados: EXECUTANDO, PARADA e PAUSADA.

        Estados tratados:
        - `EstadoAutomacao.EXECUTANDO`:
            - Indica que a automação está em execução normal.
            - Imprime uma mensagem informativa e retorna `False`, sinalizando que nenhuma modificação é necessária.

        - `EstadoAutomacao.PARADA`:
            - Indica que a automação foi interrompida.
            - Imprime uma mensagem informativa e retorna `True`, indicando que a automação deve ser encerrada.

        - `EstadoAutomacao.PAUSADA`:
            - Indica que a automação está temporariamente suspensa.
            - Imprime mensagens informativas e aguarda um evento que altere o estado para algo diferente de PAUSADA.
            - Após a mudança de estado, a função se chama recursivamente para verificar o novo estado.

        Returns:
            bool:
            - `True` se a automação deve ser encerrada.
            - `False` se a automação está executando normalmente.

        Exemplo de Uso:
        ```python
        resultado = await objeto.verificar_modificacao_status_automacao()
        if resultado:
            print("Encerrando a automação.")
        else:
            print("Automação continua em execução.")
        ```

        """
        if self.estado_automacao == EstadoAutomacao.EXECUTANDO:
            print("Estado da Automação: EXECUTANDO.")
            return False

        if self.estado_automacao == EstadoAutomacao.PARADA:
            print("Estado da Automação PARADO.")
            print("Esta automação será encerrada.")
            return True

        if self.estado_automacao == EstadoAutomacao.PAUSADA:
            print("Estado da Automação PAUSADA.")
            print("Aguardando retomar.")
            try:
                await self.wait_for_and_state_controller(lambda d: self.estado_automacao != EstadoAutomacao.PAUSADA)
            except J2RobotErro as e:
                print("Estado da Automação PARADO.")
                print("Esta automação será encerrada.")
                return True
            finally:
                return await self.verificar_modificacao_status_automacao()


