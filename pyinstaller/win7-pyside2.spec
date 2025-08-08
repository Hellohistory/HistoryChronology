# pyinstaller/win7-pyside2.spec
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
ROOT = Path(__file__).resolve().parent.parent  # 项目根目录
RES_DIR = ROOT / "resources"                   # 你的 QSS / ICO 等资源
LIC_DIR = ROOT / "licenses"                    # 建议把三方许可文本放到这个目录
ICON_PATH = RES_DIR / "logo.ico"               # 可选图标

# —— 数据文件收集：resources / licenses / opencc 数据 ——
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

# opencc-python-reimplemented 纯 Python实现，但也带有数据文件
datas += collect_data_files("opencc", include_py_files=True)

# —— 隐式模块与动态库（Qt 平台插件） ——
hiddenimports = []
hiddenimports += collect_submodules("opencc")

# PySide2 的动态库（如 qwindows.dll）交给钩子自动收集；再保险可显式收集
binaries = collect_dynamic_libs("PySide2")

block_cipher = None

a = Analysis(
    ["entry_pyside2.py"],
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
    name="ShijianWin7",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 窗口程序
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
)

# 单文件模式（-F）
coll = COLLECT(exe, name="ShijianWin7")
