import asyncio
import threading
import psutil
import os


from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import json

from core.robo import robo, iniciar_robo
from utils.env import ENV_WEB_APP_BUNDLES, ENV_WEB_APP_BUNDLES_BUILD_FOLDER
from utils.path import get_resource_path

frontend_bundles= get_resource_path(ENV_WEB_APP_BUNDLES, build_folder=ENV_WEB_APP_BUNDLES_BUILD_FOLDER)

app = Flask(__name__, static_folder=frontend_bundles)

# Função para carregar configurações salvas
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Função para salvar configurações no arquivo
def save_config(config_data):
    with open('config.json', 'w') as file:
        json.dump(config_data, file)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/index-old')
def index_old():
    config = load_config()
    #config_page_path = get_resource_path("app_web/config_page.html")
    #return render_template(config_page_path, config=config)
    return render_template('config_page.html', config=config)

@app.route('/save_config', methods=['POST'])
def save():
    config_data = {
        'speed': request.form['speed'],
        'mode': request.form['mode'],
    }
    save_config(config_data)
    return redirect(url_for('index'))

@app.route('/start_robot')
def start_robot():
    iniciar_robo()
    print("Thread do robô iniciada!")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


def iniciar_servidor(thread_autonoma=False):
    if thread_autonoma:
        threading.Thread(target=iniciar_servidor, args=(False,), daemon=True).start()
    else:
        app.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    iniciar_servidor()
