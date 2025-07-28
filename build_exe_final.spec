# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# カレントディレクトリを取得
current_dir = Path.cwd()

# PyInstaller用のフック設定
hookspath = []
hooksconfig = {}

# CustomTkinterのパスを動的に検出
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    ctk_assets = os.path.join(ctk_path, 'assets')
    if os.path.exists(ctk_assets):
        datas = [(ctk_assets, 'customtkinter/assets')]
    else:
        datas = []
except ImportError:
    datas = []

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'customtkinter',
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
        'sys',
        'json',
        'typing',
    ],
    hookspath=hookspath,
    hooksconfig=hooksconfig,
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'scipy', 'jupyter', 'IPython'],
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
    version=None,
)
