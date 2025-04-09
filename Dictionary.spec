# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# === Paths ===
project_root = Path(sys.argv[0]).resolve().parent
resources_dir = project_root / "resources"
icons_dir = resources_dir / "icons"
styles_dir = resources_dir / "styles"

# === Bundle Static Assets ===
datas = [
    (str(icons_dir / "app_icon.ico"), "resources/icons"),
    (str(icons_dir / "search_icon.svg"), "resources/icons"),
    (str(styles_dir / "stylesheet.qss"), "resources/styles"),
]

# === Handle NLTK Hidden Imports ===
hidden_imports = collect_submodules("nltk.corpus") + [
    "nltk",
    "nltk.data",
    "nltk.corpus",
    "nltk.corpus.reader.api",
    "nltk.corpus.reader.wordnet",
]

# === PyInstaller Build Steps ===
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', '_tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Dictionary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icons_dir / "app_icon.ico"),
    single_file=True
)
