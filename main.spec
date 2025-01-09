# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

import os
import dotenv

dotenv.load_dotenv()
ENV_BUILD_FOLDER = os.getenv("BUILD_FOLDER")
ENV_EXE_NAME = os.getenv("EXE_NAME")

not_allowed_not_packagable_extensions = ( ".py" )

binaries = [
    ("artifacts", "artifacts"),
]

data_not_packagable = [
    ('fluxo', 'fluxo'),
    ("artifacts", "artifacts"),
]

data_packagable = [
    ("pje/ng2/dev_menu_automacao.html", "pje/ng2"),
    ("pje/ng2/dev_menu_automacao.js", "pje/ng2"),
    (".env", ".")
]


def print_datas(datas, identificador=None):
    print(f"Tamanho datas{ f" id:'{identificador}'" if not identificador is None else ""}: {len(datas)}")
    print("-" * 60)
    for a_it, b, c in datas:
        print(f"{a_it} |||| {b} |||| {c}")
    print("-" * 60)

a_to_data_not_packagable = Analysis(
    ['main.py'],
    datas=data_not_packagable,
    binaries=binaries,
    noarchive=False,
    optimize=0,
)
print_datas(a_to_data_not_packagable.datas, "arquivos_nao_empacotaveis")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=data_packagable,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=ENV_EXE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
print_datas(a.datas, "arquivos_pacotaveis")


allowed_paths = tuple(item[1] for item in data_not_packagable)
filtered_datas = list(filter(lambda d: d[0].startswith(allowed_paths) and not d[0].endswith(
    not_allowed_not_packagable_extensions
    ), a_to_data_not_packagable.datas))
filtered_binaries = list(filter(lambda d: d[0].startswith(allowed_paths), a_to_data_not_packagable.binaries))

coll = COLLECT(
    exe,
    filtered_datas,
    filtered_binaries,
    name=ENV_BUILD_FOLDER,
    strip=False,
    upx_exclude=[],
    upx=True,
)

