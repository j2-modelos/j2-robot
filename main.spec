# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

def print_datas(datas, identificador=None):
    print(f"Tamanho datas{ f" id:'{identificador}'" if not identificador is None else ""}: {len(datas)}")
    print("-" * 60)
    for a_it, b, c in datas:
        print(f"{a_it} |||| {b} |||| {c}")
    print("-" * 60)

a_to_make_configurable_files = Analysis(
    ['main.py'],
    datas=[('fluxo/*', 'fluxo')],
    noarchive=False,
    optimize=0,
)
print_datas(a_to_make_configurable_files.datas, "arquivos_configuração")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("artifacts/*", "artifacts"),
        ("pje/ng2/dev_menu_automacao.html", "pje/ng2"),
        ("pje/ng2/dev_menu_automacao.js", "pje/ng2"),
        (".env", ".")
    ],
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
    name='main',
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
print_datas(a.datas, "principal")

fluxo_datas = list(filter(lambda d: d[0].startswith("fluxo") and d[0].endswith((".xlsx", ".html")), a_to_make_configurable_files.datas ))

coll = COLLECT(
    exe,
    fluxo_datas,
    name='j2-robot-2',

    strip=False,
    upx_exclude=[],
    upx=True,
)
