"""
支持通过命令行参数选择 PySide2 或 PySide6 UI 后端。
"""
import sys
import argparse
from pathlib import Path
import requests

import config


def download_db(db_path: Path, url: str) -> None:
    """
    下载数据库文件到本地，如果文件不存在则从远程获取
    :param db_path: 本地数据库文件路径
    :param url: 远程数据库下载地址
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(db_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def main() -> None:
    """
    应用程序主入口，解析参数、检查数据库、加载样式、创建并运行主窗口
    """
    # 1. 使用 argparse 来接收命令行参数
    parser = argparse.ArgumentParser(description="史鉴 - 中华甲子历史年表")
    parser.add_argument(
        '--ui',
        type=str,
        choices=['pyside2', 'pyside6'],
        required=True,
        help="选择要使用的UI库 (pyside2 for Win7, pyside6 for Win10+)"
    )
    args = parser.parse_args()

    # 2. 动态导入正确的UI库和主窗口
    if args.ui == 'pyside6':
        print("正在加载 PySide6 UI...")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from ui_pyside6.main_window import MainWindow
    else:  # args.ui == 'pyside2'
        print("正在加载 PySide2 UI...")
        from PySide2.QtWidgets import QApplication
        from PySide2.QtGui import QIcon
        from ui_pyside2.main_window import MainWindow

    # 3. 后续的逻辑
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        try:
            print(f"数据库文件 {db_path} 不存在，正在从远程下载...")
            download_db(db_path, config.REMOTE_DB_URL)
            print("数据库下载完成。")
        except Exception as e:
            print(f"数据库下载失败：{e}")
            sys.exit(1)

    app = QApplication(sys.argv)

    icon_path = Path(config.ICON_PATH)
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        print(f"警告：应用图标文件未找到：{icon_path}")

    qss_path = config.LIGHT_STYLE_QSS
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    # MainWindow 来自于之前动态导入的模块
    win = MainWindow(db_path=str(db_path))
    win.resize(1000, 650)
    win.show()

    if args.ui == 'pyside6':
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
