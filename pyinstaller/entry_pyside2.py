# pyinstaller/entry_pyside2.py

import sys
from ui_pyside2.main_window import MainWindow
from PySide2.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    db_path = "resources/History_Chronology.db"
    window = MainWindow(db_path)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
