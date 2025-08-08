# entry_pyside2.py
# -*- coding: utf-8 -*-
"""
独立入口（Win7）：PySide2 版本
用法（开发态）: python entry_pyside2.py
PyInstaller:    pyinstaller -F -n ShijianWin7 entry_pyside2.py
"""

from __future__ import annotations

from app_bootstrap import run_app


def main() -> None:
    """应用入口（PySide2）"""
    run_app("pyside2")


if __name__ == "__main__":
    main()
