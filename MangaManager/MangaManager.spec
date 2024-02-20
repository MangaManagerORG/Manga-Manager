# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['PIL._tkinter_finder','tkinterdnd2.TkinterDnD']
collects = [collect_all('sv_ttk'),collect_all('tkinterdnd2')]
for ret in collects:
    datas += ret[0]
    binaries += ret[1]
    hiddenimports += ret[2]

block_cipher = None
added_files = [
         ( 'res/*', 'res'),
         ('ExternalSources', 'ExternalSources'),
         ('Extensions', 'Extensions')
         ] +datas

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=['pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MangaManager',
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
    icon=['res/icon.ico'],
)
