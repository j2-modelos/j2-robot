import asyncio

class RoboControl:
    def __init__(self):
        # Evento para controlar a execução da tarefa robô
        self.rob_event = asyncio.Event()  # Controle de pausa para o robô
        self.rob_event.set()  # Inicialmente, o evento está 'set', ou seja, pode continuar

        # Evento para controlar a execução do WebSocket (separado do robô)
        self.ws_event = asyncio.Event()  # Controle para o WebSocket
        self.ws_event.set()  # WebSocket pode continuar

        self.robo_task = None  # Tarefa global única do robô

    async def tarefa1(self):
        # Simula a execução da tarefa1 do robô com 100 repetições
        for i in range(100):
            print(f"Executando tarefa1: etapa {i + 1}")
            await self.trabalhando(i)
            await self.check_pausa()  # Verifica a pausa a cada etapa do loop
        print("Tarefa1 finalizada!")

    async def tarefa2(self):
        # Simula a execução da tarefa2 do robô
        for i in range(3):
            print(f"Executando tarefa2: etapa {i + 1}")
            await self.trabalhando(i)
            await self.check_pausa()  # Verifica a pausa a cada etapa do loop
        print("Tarefa2 finalizada!")

    async def trabalhando(self, i):
        await asyncio.sleep(1)  # Simula o tempo de trabalho da tarefa

    async def check_pausa(self):
        """Verifica se o robô precisa ser pausado durante uma tarefa longa."""
        await self.rob_event.wait()  # Verifica se o robô deve continuar (ou se está pausado)

    async def pausar_robo(self):
        print("Robô pausado!")
        self.rob_event.clear()  # Pausa a execução do robô (bloqueia todas as corrotinas associadas ao evento)

    async def continuar_robo(self):
        print("Robô retomado!")
        self.rob_event.set()  # Retoma a execução do robô (desbloqueia todas as corrotinas associadas ao evento)

    async def pausar_websocket(self):
        print("WebSocket pausado!")
        self.ws_event.clear()  # Pausa a execução do WebSocket

    async def continuar_websocket(self):
        print("WebSocket retomado!")
        self.ws_event.set()  # Retoma a execução do WebSocket

    async def parar(self):
        print("Robô interrompido!")
        if self.robo_task:
            self.robo_task.cancel()  # Cancela a tarefa global do robô

    async def iniciar(self, corrotina):
        # Recebe a corrotina a ser executada como tarefa
        if not callable(corrotina):
            raise ValueError("A tarefa fornecida não é uma corrotina válida!")

        # Cria a tarefa global passando a corrotina fornecida
        self.robo_task = asyncio.create_task(corrotina())  # Cria e executa a tarefa
        await self.robo_task  # Aguarda a execução da corrotina

    async def controlar_websocket(self):
        # Função para controlar o WebSocket sem bloquear a execução do robô
        while True:
            await self.ws_event.wait()  # Verifica se o WebSocket pode continuar
            print("Escutando mensagens do WebSocket...")
            await asyncio.sleep(5)  # Simula o tempo de espera até a próxima mensagem

            # Caso queira verificar um comando de pausa durante a execução do WebSocket
            if not self.rob_event.is_set():
                print("WebSocket interrompido porque o robô está pausado")

            await asyncio.sleep(0.1)  # Adiciona delay de espera para evitar uso excessivo de CPU

    async def controle_por_prompt(self):
        print("Comandos disponíveis:")
        print(" - 'iniciar tarefa1' para iniciar a tarefa1")
        print(" - 'iniciar tarefa2' para iniciar a tarefa2")
        print(" - 'pausar robô' para pausar o robô")
        print(" - 'continuar robô' para continuar a execução do robô")
        print(" - 'pausar websocket' para pausar o WebSocket")
        print(" - 'continuar websocket' para continuar o WebSocket")
        print(" - 'parar' para parar o robô")

        while True:
            comando = input("Digite um comando: ").strip().lower()

            if comando == "iniciar tarefa1":
                await self.iniciar(self.tarefa1)
            elif comando == "iniciar tarefa2":
                await self.iniciar(self.tarefa2)
            elif comando == "pausar robô":
                await self.pausar_robo()
            elif comando == "continuar robô":
                await self.continuar_robo()
            elif comando == "pausar websocket":
                await self.pausar_websocket()
            elif comando == "continuar websocket":
                await self.continuar_websocket()
            elif comando == "parar":
                await self.parar()
                break  # Sai do loop quando o robô for interrompido
            else:
                print("Comando desconhecido. Tente novamente.")


# Exemplo de ponto onde você já tem um loop asyncio existente

async def main():
    robo_control = RoboControl()
    # Criando as corrotinas sem rodar asyncio.run no loop principal
    task_websocket = asyncio.create_task(robo_control.controlar_websocket())  # Escutando o WebSocket
    task_prompt = asyncio.create_task(robo_control.controle_por_prompt())  # Controle via prompt

    # Adicionando uma tarefa global (tarefa1 ou tarefa2)
    await robo_control.iniciar(robo_control.tarefa1)

    # Espera por ambas as tarefas, porém o controle via prompt pode interagir
    await asyncio.gather(task_websocket, task_prompt)

if __name__ == "__main__":
    # Aqui você não usa asyncio.run() porque seu loop já pode estar em execução
    asyncio.run(main())
