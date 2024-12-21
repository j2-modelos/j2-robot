import asyncio
import websockets
import json
from asyncio import Queue

from utils.mensagem import Mensagem, from_json


class WebSocketServerClient:
    def __init__(self, host='localhost', port=8765):
        """Inicializa a classe para operar como servidor e cliente WebSocket utilizando a mesma porta"""
        self.host = host
        self.port = port
        self.websocket = None
        self.message_queue = Queue()  # Fila para armazenar as mensagens recebidas

    async def handler(self, websocket):
        """Manipulador para o WebSocket servidor: ouvir comandos do cliente externo e responder"""
        print(f'Novo cliente conectado: {websocket}')

        # Envia uma mensagem de boas-vindas ao cliente
        await websocket.send("Conexão estabelecida com o servidor WebSocket!")

        try:
            # Aguarda as mensagens enviadas pelo cliente (externo)
            async for message in websocket:
                print(f"Mensagem recebida do cliente: {message}")
                # Coloca a mensagem na fila
                await self.message_queue.put(message)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Conexão encerrada com o cliente: {e}")

    async def start_server(self):
        """Inicia o servidor WebSocket (escutando novos clientes externos na mesma porta)"""
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Servidor WebSocket iniciado em {self.host}:{self.port}")
        await server.wait_closed()

    async def connect_client(self):
        """Conecta-se ao servidor WebSocket como cliente e escuta comandos"""
        url = f"ws://localhost:{self.port}"  # Conecta-se ao servidor WebSocket na mesma porta
        self.websocket = await websockets.connect(url)

        print(f"Conectado ao WebSocket na porta {self.port} como cliente")

        # Envia uma mensagem ao servidor
        await self.websocket.send("Mensagem do cliente para o servidor!")

        # Aguarda comandos do servidor
        async for message in self.websocket:
            print(f"Comando recebido do servidor: {message}")

    async def ouvir_mensagens(self) -> Mensagem | None:
        """Aguarda uma mensagem do cliente externo na fila e tenta parsear como JSON"""
        # Aguarda até que uma mensagem esteja na fila
        message = await self.message_queue.get()

        return from_json(message)

    async def run(self):
        """Executa o servidor e cliente WebSocket simultaneamente na mesma porta"""
        server_task = asyncio.create_task(self.start_server())  # Tarefa do servidor
        #client_task = asyncio.create_task(self.connect_client())  # Tarefa do cliente

        # Aguarda ambas as tarefas serem concluídas
        #await asyncio.gather(server_task, client_task)
        await server_task

    def start(self):
        """Inicia a execução da aplicação como servidor e cliente WebSocket utilizando a mesma porta"""
        # Cria e executa o loop assíncrono
        asyncio.create_task(self.run())