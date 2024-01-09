# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
added_files = [
         ( 'res/*', 'res'),
         ('ExternalSources', 'ExternalSources'),
         ('Extensions', 'Extensions'),
         # THe following are picked from env variable. Please run python to include possible missing files
         ('../venv_3.11/Lib/site-packages/sv_ttk/*','sv_ttk'), # To save the sv_ttk.tcl file - MISSING IMPORT
         ('../venv_3.11/Lib/site-packages/sv_ttk/theme*','sv_ttk/theme'), # To save the sv_ttk.tcl file - MISSING IMPORT
         ('../venv_3.11/Lib/site-packages/open_clip/model_configs/ViT-B-16-plus-240.json','open_clip/model_configs'), # To save the sv_ttk.tcl file - MISSING IMPORT
         ('../venv_3.11/Lib/site-packages/open_clip/bpe_simple_vocab_16e6.txt.gz','open_clip') # To save the sv_ttk.tcl file - MISSING IMPORT

         ]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['PIL._tkinter_finder','tkinterdnd2.TkinterDnD'],
    hookspath=['MangaManager/pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    paths=["venv_3.11/Lib/site-packages"] # So it loads libraries from dev env first
#    collect_all=True
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
