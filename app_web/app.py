from app_web.server import app, iniciar_servidor
from app_web.tray import icon, iniciar_icon_tray


def iniciar_web_app():
    iniciar_servidor(thread_autonoma=True)
    iniciar_icon_tray()

if __name__ == '__main__':
    iniciar_web_app()
