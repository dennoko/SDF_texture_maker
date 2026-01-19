# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# カレントディレクトリを取得
current_dir = Path.cwd()

# PyInstaller用のフック設定
hookspath = []
hooksconfig = {}

# パスとデータ収集の設定
datas = []

# CustomTkinter
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    ctk_assets = os.path.join(ctk_path, 'assets')
    if os.path.exists(ctk_assets):
        datas.append((ctk_assets, 'customtkinter/assets'))
except ImportError:
    pass

# tkinterdnd2
try:
    import tkinterdnd2
    tkdnd2_path = os.path.dirname(tkinterdnd2.__file__)
    datas.append((tkdnd2_path, 'tkinterdnd2'))
except ImportError:
    pass

# Add src/resources
resources_path = os.path.join(current_dir, 'src', 'resources')
if os.path.exists(resources_path):
    datas.append((str(resources_path), 'src/resources'))

# Add icon
icon_path = os.path.join(current_dir, 'icon')
if os.path.exists(icon_path):
    datas.append((str(icon_path), 'icon'))

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
        'tkinterdnd2',
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
        'watchdog.observers.read_directory_changes',
        'watchdog.observers.polling',
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
    name='SDF_Make_Supporter',
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
    icon=['icon\\\\icon.ico'],
    version=None,
)
