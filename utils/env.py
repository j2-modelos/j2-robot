import os
import dotenv

from utils.path import get_resource_path

default_env_path = get_resource_path(".env")
dotenv.load_dotenv(default_env_path)

ENV_J2_EXTENSAO_VERSAO = os.getenv("J2_EXTENSAO_VERSAO")
ENV_CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
ENV_J2_EXTENSION_PATH = os.getenv("J2_EXTENSION_PATH")
ENV_CHROME_USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR")
ENV_PERFIL_CHROME = os.getenv("PERFIL_CHROME")
ENV_CHAT_GPT_URL = os.getenv("CHAT_GPT_URL")
ENV_PJE_PAYLOAD_WEB_ROOT = os.getenv("PJE_PAYLOAD_WEB_ROOT")

ENV_BUILD_FOLDER = os.getenv("BUILD_FOLDER")
ENV_EXE_NAME = os.getenv("EXE_NAME")
