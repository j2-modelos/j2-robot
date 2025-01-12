import os
import dotenv

from utils.path import get_resource_path
from utils.tipos import normalizar_valor_boolean

envs = [
    (".env", True),
    (".env.chrome", False),
    ("fluxo/.env.fluxo", False),
    #todo: aqui
    ("app_web/.env.app_web", True)
]

for env_path, packaged in envs:
    dotenv.load_dotenv(get_resource_path(env_path, packaged))

ENV_J2_EXTENSAO_VERSAO = os.getenv("J2_EXTENSAO_VERSAO")
ENV_CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
ENV_J2_EXTENSION_PATH = os.getenv("J2_EXTENSION_PATH")
ENV_CHROME_USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR")
ENV_DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")
ENV_PERFIL_CHROME = os.getenv("PERFIL_CHROME")
ENV_CHAT_GPT_URL = os.getenv("CHAT_GPT_URL")
ENV_PJE_PAYLOAD_WEB_ROOT = os.getenv("PJE_PAYLOAD_WEB_ROOT")

ENV_BUILD_FOLDER = os.getenv("BUILD_FOLDER")
ENV_EXE_NAME = os.getenv("EXE_NAME")

ENV_AVALIACAO_MULTI_SELECAO_MODO_VALIDACAO = normalizar_valor_boolean(os.getenv("AVALIACAO_MULTI_SELECAO_MODO_VALIDACAO"))

#todo: aqui
ENV_WEB_APP_BUNDLES = os.getenv("WEB_APP_BUNDLES")
ENV_WEB_APP_BUNDLES_BUILD_FOLDER = os.getenv("WEB_APP_BUNDLES_BUILD_FOLDER")
