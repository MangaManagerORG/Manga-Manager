# from update_version import update_version_file
# update_version_file()
from MangaManager.MangaManager.__version__ import __version__ as version_
from platform import system
from datetime import date
from datetime import datetime
build_version = version_.split(":")[-1]
build_date = date.today()
release_name = "_".join(
    ["MangaManager",
     str(build_date.year),
     str(build_date.month).zfill(2),
     str(build_date.day).zfill(2),
     str(datetime.now().hour).zfill(2),
     str(datetime.now().minute).zfill(2),
     str(datetime.now().second).zfill(2),
     system(), build_version, "_Cuda"])
# from PyInstaller.utils.hooks import collect_all

# datas = collect_all('open_clip')
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
         ( 'res/*', 'res'),
         ('ExternalSources', 'ExternalSources'),
         ('Extensions', 'Extensions'),
         # THe following are picked from env variable. Please run python to include possible missing files
         ('../.venv/Lib/site-packages/open_clip/model_configs/ViT-B-16-plus-240.json','open_clip/model_configs'), # To save the sv_ttk.tcl file - MISSING IMPORT
         ('../.venv/Lib/site-packages/open_clip/bpe_simple_vocab_16e6.txt.gz','open_clip') # To save the sv_ttk.tcl file - MISSING IMPORT

         ],
    hiddenimports=['PIL._tkinter_finder','tkinterdnd2.TkinterDnD','slugify'],
    hookspath=['MangaManager/pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    paths=["venv_3.11/Lib/site-packages"] # So it loads libraries from dev env first
#    collect_all=True
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=release_name,
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=['res/icon.ico'],
)

coll_Cuda = COLLECT(exe,
               a.binaries,
               a.datas,
               strip=None,
               upx=True,
               name=release_name)