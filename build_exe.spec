# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# カレントディレクトリを取得
current_dir = Path.cwd()

# CustomTkinterのデータファイルを含める
datas = []
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    ctk_assets = os.path.join(ctk_path, 'assets')
    if os.path.exists(ctk_assets):
        datas.append((ctk_assets, 'customtkinter/assets'))
except ImportError:
    pass

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'customtkinter',
        'customtkinter.windows',
        'customtkinter.windows.widgets',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageFilter',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'numpy',
        'cv2',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'pathlib',
        'threading',
        'time',
        'os',
        'typing',
        'typing_extensions',
        'darkdetect',
        'distutils',
        'distutils.util',
        'distutils.version',
        'setuptools',
        'setuptools.dist',
        'packaging',
        'packaging.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
        'pytest',
        'unittest',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SDF_Texture_Maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # コンソールを表示しない
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定
)
