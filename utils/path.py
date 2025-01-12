import os
import sys


def get_resource_path(resource_name, packaged=True, build_folder=None):
    """Obtém o caminho correto para o arquivo de recurso,
    levando em consideração se estamos em 'onefile' ou 'onedir',
    ou se o parâmetro 'packaged' está True ou False."""

    if getattr(sys, 'frozen', False):  # Está em ambiente PyInstaller
        if packaged:
            # No modo onefile (quando o PyInstaller extrai os arquivos para um diretório temporário)
            if hasattr(sys, '_MEIPASS'):
                path = [sys._MEIPASS, resource_name if build_folder is None else build_folder]
                resource_path = os.path.join(*path)
            else:
                # Quando o modo onedir é usado, o recurso estará ao lado do executável
                resource_path = os.path.join(os.path.dirname(sys.executable),  resource_name)
        else:
            # Quando 'packaged' é False, busca diretamente no diretório ao lado do executável
            resource_path = os.path.join(os.path.dirname(sys.executable), '_internal', resource_name)
    else:
        # Durante o desenvolvimento, quando o código está sendo executado diretamente do script
        resource_path = os.path.join(os.path.dirname(__file__), os.path.pardir, resource_name)

    resource_path = os.path.normpath(resource_path).replace("\\", "/")

    return resource_path