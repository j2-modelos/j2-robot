import os

# Caminho para a raiz do projeto (diretório onde este script está localizado)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Caminho do arquivo específico na raiz do projeto
for rel_path in ['.dist/j2-robot.exe', '.dist/j2-robot.zip']:
    file_path = os.path.join(root_dir, rel_path)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f'O arquivo {file_path} foi deletado com sucesso.')
    else:
        print(f'O arquivo {file_path} não foi encontrado.')