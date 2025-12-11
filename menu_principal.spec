# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

a = Analysis(
    ['menu_principal.py'],
    pathex=['C:\\Users\\Cheko\\Downloads\\pytons\\Sifilis'],
    binaries=[],
    datas=[
        ('estilos.py', '.'),
        ('utilidades.py', '.'),
        ('modelo_a.py', '.'),
        ('modelo_b.py', '.'),
        ('gestor_datos.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkcalendar',
        'pandas',
        'numpy',
        'sklearn',
        'sklearn.linear_model',
        'openpyxl',
        'webbrowser',
        'subprocess',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaEpidemiologico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)