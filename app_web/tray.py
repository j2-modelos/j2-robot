import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import webbrowser
import threading
import json

from app_web.server import app
from core.robo import iniciar_robo


# Carregar as configurações
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Função para criar o ícone
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, 3 * width // 4, 3 * height // 4), fill=color2)
    return image

# Função que abre o navegador para o Flask
def on_open_web(icon, item):
    webbrowser.open("http://127.0.0.1:5000")

# Função para sair do programa
def on_quit(icon, item):
    icon.stop()

# Função para iniciar o robô via tray
def on_start_robo(icon, item):
    iniciar_robo()

# Definindo o menu do ícone
menu = (item('Abrir Interface Web', on_open_web),
        item('Iniciar Robô', on_start_robo),
        item('Sair', on_quit))

# Criando o ícone da bandeja
icon = pystray.Icon("Robô", create_image(64, 64, "blue", "white"), menu=menu)

def iniciar_icon_tray():
    icon.run()

if __name__ == '__main__':
    iniciar_icon_tray()
