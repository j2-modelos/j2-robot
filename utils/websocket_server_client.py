import asyncio
import websockets
import json
from asyncio import Queue
from utils.mensagem import Mensagem, from_json
from typing import Dict, Union

class WebSocketServerClient:
    def __init__(self, host='localhost', port=8765):
        """Inicializa a classe para operar como servidor e cliente WebSocket utilizando a mesma porta"""
        self.host = host
        self.port = port
        self.websocket = None
        self.message_queue = Queue()  # Fila para armazenar as mensagens recebidas
        self.connected_client = None  # Para armazenar o cliente conectado

    async def handler(self, websocket):
        """Manipulador para o WebSocket servidor: ouvir comandos do cliente externo e responder"""
        print(f'Novo cliente conectado: {websocket}')
        self.connected_client = websocket  # Armazena o cliente conectado

        try:
            # Envia uma mensagem de boas-vindas ao cliente
            await websocket.send("Conexão estabelecida com o servidor WebSocket!")

            # Aguarda as mensagens enviadas pelo cliente (externo)
            async for message in websocket:
                print(f"Mensagem recebida do cliente: {message}")
                # Coloca a mensagem na fila
                await self.message_queue.put(message)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Conexão encerrada com o cliente: {e}")
            self.connected_client = None  # Limpa a referência ao cliente desconectado

    async def start_server(self):
        """Inicia o servidor WebSocket (escutando novos clientes externos na mesma porta)"""
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Servidor WebSocket iniciado em {self.host}:{self.port}")
        await server.wait_closed()

    async def send_to_client(self, message: Dict[str, Union[str, int]]):
        """Envia uma mensagem para o único cliente conectado"""
        if self.connected_client:
            try:
                json_data = json.dumps(message)  # Converte o dicionário para string JSON
                await self.connected_client.send(json_data)
                print(f"Mensagem enviada ao cliente: {json_data}")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Erro ao enviar mensagem: Conexão com o cliente fechada ({e})")

    async def ouvir_mensagens(self) -> Mensagem | None:
        """Aguarda uma mensagem do cliente externo na fila e tenta parsear como JSON"""
        # Aguarda até que uma mensagem esteja na fila
        message = await self.message_queue.get()
        return from_json(message)

    async def run(self):
        """Executa o servidor WebSocket"""
        server_task = asyncio.create_task(self.start_server())  # Tarefa do servidor
        await server_task

    def start(self):
        """Inicia a execução da aplicação como servidor WebSocket"""
        asyncio.create_task(self.run())
