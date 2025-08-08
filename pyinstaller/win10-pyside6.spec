# pyinstaller/win10-pyside6.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    collect_dynamic_libs,
    copy_metadata,
)

# —— 路径设置 ——
ROOT = Path(__file__).resolve().parent.parent
RES_DIR = ROOT / "resources"
LIC_DIR = ROOT / "licenses"
ICON_PATH = RES_DIR / "logo.ico"

# —— 数据文件 ——
datas = []
if RES_DIR.exists():
    for p in RES_DIR.rglob("*"):
        if p.is_file():
            rel = p.relative_to(RES_DIR).parent.as_posix()
            datas.append((str(p), f"resources/{rel}"))

if LIC_DIR.exists():
    for p in LIC_DIR.rglob("*"):
        if p.is_file():
            rel = p.relative_to(LIC_DIR).parent.as_posix()
            datas.append((str(p), f"licenses/{rel}"))

datas += collect_data_files("opencc", include_py_files=True)

# —— 隐式模块与动态库 ——
hiddenimports = []
hiddenimports += collect_submodules("opencc")

binaries = collect_dynamic_libs("PySide6")

block_cipher = None

a = Analysis(
    ["entry_pyside6.py"],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
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
    name="ShijianWin10",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
)

coll = COLLECT(exe, name="ShijianWin10")
