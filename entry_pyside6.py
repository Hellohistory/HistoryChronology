# entry_pyside6.py
# -*- coding: utf-8 -*-
"""
独立入口（Win10/11）：PySide6 版本
用法（开发态）: python entry_pyside6.py
PyInstaller:    pyinstaller -F -n ShijianWin10 entry_pyside6.py
"""

from __future__ import annotations

from app_bootstrap import run_app


def main() -> None:
    """应用入口（PySide6）"""
    run_app("pyside6")


if __name__ == "__main__":
    main()
