# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# === Project Directories ===
project_root = Path(sys.argv[0]).resolve().parent

datas = [
    ('resources/icons/app_icon.ico', 'resources/icons'),
    ('resources/icons/search_icon.svg', 'resources/icons'),
    ('resources/styles/stylesheet.qss', 'resources/styles')
]

# === Hidden Imports for NLTK WordNet support ===
hidden_imports = collect_submodules("nltk.corpus") + [
    "nltk",
    "nltk.data",
    "nltk.downloader",
    "nltk.corpus",
    "nltk.corpus.reader.api",
    "nltk.corpus.reader.wordnet",
    "nltk.tokenize",
    "nltk.tokenize.punkt",
]

# === Analysis: main script + resource configs ===
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
    optimize=0,
)

# === PYZ Archive (pure Python code) ===
pyz = PYZ(a.pure)

# === Executable Settings ===
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Dictionary',
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
    icon=['resources\\icons\\app_icon.ico'],
)
