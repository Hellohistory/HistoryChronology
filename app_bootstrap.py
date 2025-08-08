# app_bootstrap.py
# -*- coding: utf-8 -*-
"""
公共引导模块：按后端(PySide2/PySide6)启动应用，负责 DB 就绪、样式加载与事件循环。
放在项目根目录，避免大规模改动 import 路径。
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Literal, Optional

import requests

import config


def _sha256_file(path: Path) -> str:
    """计算本地文件的 SHA256（用于下载后校验完整性）"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _download_db(db_path: Path, url: str, expected_sha256: Optional[str] = None) -> None:
    """
    下载数据库到本地；如提供 expected_sha256 则进行校验
    """
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    tmp = db_path.with_suffix(".downloading")
    with open(tmp, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    if expected_sha256:
        actual = _sha256_file(tmp)
        if actual.lower() != expected_sha256.lower():
            tmp.unlink(missing_ok=True)
            raise ValueError(f"DB 校验失败：期望 {expected_sha256}，实际 {actual}")
    tmp.replace(db_path)


def run_app(ui_backend: Literal["pyside2", "pyside6"]) -> None:
    """
    启动应用：根据 ui_backend 选择 PySide2 / PySide6。
    仅作为入口脚本的调度函数被调用。
    """
    if ui_backend == "pyside6":
        # —— PySide6 路径（Win10/11）——
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from ui_pyside6.main_window import MainWindow
        is_py6 = True
    else:
        # —— PySide2 路径（Win7）——
        from PySide2.QtWidgets import QApplication
        from PySide2.QtGui import QIcon
        from ui_pyside2.main_window import MainWindow
        is_py6 = False

    # —— 确保数据库就绪（支持可选 SHA256 校验）——
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        print(f"[INFO] 数据库缺失，正在下载到：{db_path}")
        expected = getattr(config, "REMOTE_DB_SHA256", None)
        _download_db(db_path, config.REMOTE_DB_URL, expected)
        print("[INFO] 数据库下载完成。")

    # —— 初始化 Qt 应用、加载样式和图标 ——
    app = QApplication(sys.argv)

    try:
        app.setStyle("Fusion")
    except Exception:
        pass

    icon_path = Path(config.ICON_PATH)
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        print(f"[WARN] 应用图标文件未找到：{icon_path}")

    qss_path = config.LIGHT_STYLE_QSS
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # —— 主窗口 ——
    win = MainWindow(db_path=str(db_path))
    win.resize(1000, 650)
    win.show()

    # —— 事件循环 ——
    if is_py6:
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())
