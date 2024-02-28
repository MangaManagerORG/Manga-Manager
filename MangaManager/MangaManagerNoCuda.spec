# from update_version import update_version_file
# update_version_file()
import os
import pathlib
import platform
from MangaManager.MangaManager.__version__ import __version__ as version_
from platform import system
from datetime import date
from datetime import datetime
build_version = version_.split(":")[-1]
build_date = date.today()
VENV = os.getenv("VIRTUAL_ENV")
if platform.system() == "Windows":
    venv_path = VENV + "/Lib"
else:
    venv_path = VENV + "/lib/python3.11"

release_name = "_".join(
    ["MangaManager",
     str(build_date.year),
     str(build_date.month).zfill(2),
     str(build_date.day).zfill(2),
     str(datetime.now().hour).zfill(2),
     str(datetime.now().minute).zfill(2),
     str(datetime.now().second).zfill(2),
     system(), build_version, "_NoCuda"])
open_clip_libs = []
    # (venv_path + '/site-packages/open_clip/model_configs/ViT-B-16-plus-240.json','open_clip/model_configs'), # To save the sv_ttk.tcl file - MISSING IMPORT
    #             (venv_path + '/site-packages/open_clip/bpe_simple_vocab_16e6.txt.gz','open_clip')] if pathlib.Path(venv_path,"site-packages","open_clip").exists() else [] # To save the sv_ttk.tcl file - MISSING IMPORT],
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
         ( 'res/*', 'res'),
         ('ExternalSources', 'ExternalSources'),
         ('Extensions', 'Extensions'),
         ] + open_clip_libs,
    hiddenimports=['PIL._tkinter_finder','tkinterdnd2.TkinterDnD','slugify'],
    hookspath=['MangaManager/pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch','numpy','cv2','open_clip','torchvision','torchaudio','tensorflow'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    # paths=[venv_path +"/site-packages"] # So it loads libraries from dev env first
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

coll_NoCuda = COLLECT(exe,
               a.binaries,
               a.datas,
               strip=None,
               upx=True,
               name=release_name)