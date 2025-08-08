# ui_pyside6/main_window.py
"""
主窗口：PySide6 版本
"""
from __future__ import annotations
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QPoint, QSettings
from PySide6.QtGui import QCursor, QAction
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox,
                               QPushButton, QTableWidgetItem, QToolTip, QVBoxLayout, QWidget, QDialog,
                               QAbstractItemView)

import config
from core.data.repository import ChronologyRepository
from core.models.history_entry import HistoryEntry
from core.services.chronology_service import ChronologyService
from ui_pyside6.dialogs.advanced_search_dialog import AdvancedSearchDialog
from ui_pyside6.widgets.copyable_table_widget import CopyableTableWidget

YEAR_MIN, YEAR_MAX = config.YEAR_MIN, config.YEAR_MAX
GITHUB_URL = "https://github.com/Hellohistory/OpenPrepTools"
GITEE_URL = "https://gitee.com/Hellohistory/OpenPrepTools"


class MainWindow(QMainWindow):
    """主窗口 (PySide6)"""

    def __init__(self, db_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("史鉴 (for Windows 10/11)")
        self.settings = QSettings("Hellohistory", "ShiJian")
        repo = ChronologyRepository(db_path)
        self._svc = ChronologyService(repo)
        self._create_menu()
        self._build_ui()
        theme_path_str = self.settings.value("theme", str(config.LIGHT_STYLE_QSS))
        self._apply_theme(Path(theme_path_str))

    def _create_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        exit_act = QAction("退出", self);
        exit_act.setShortcut("Ctrl+Q");
        exit_act.triggered.connect(self.close);
        file_menu.addAction(exit_act)
        view_menu = menubar.addMenu("界面主题")
        themes = [("浅色", config.LIGHT_STYLE_QSS), ("黑暗", config.DARK_STYLE_QSS), ("蓝色", config.BLUE_STYLE_QSS),
                  ("绿色", config.GREEN_STYLE_QSS), ("橙色", config.ORANGE_STYLE_QSS),
                  ("高对比", config.HIGHCONTRAST_STYLE_QSS), ("Solarized", config.SOLARIZED_STYLE_QSS)]
        for name, qss_path in themes:
            act = QAction(name, self);
            act.triggered.connect(lambda checked=False, p=qss_path: self._apply_theme(p));
            view_menu.addAction(act)
        help_menu = menubar.addMenu("帮助")
        about_act = QAction("关于", self);
        about_act.triggered.connect(self._show_about);
        help_menu.addAction(about_act)
        thanks_act = QAction("感谢", self);
        thanks_act.triggered.connect(self._show_thanks);
        help_menu.addAction(thanks_act)

    def _apply_theme(self, qss_path: Path) -> None:
        app = QApplication.instance()
        app.setStyle("Fusion")
        if qss_path.exists():
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"));
            self.settings.setValue("theme", str(qss_path))
        else:
            print(f"警告：未找到主题文件 {qss_path}")

    def _show_about(self) -> None:
        QMessageBox.about(self, "关于",
                          f"<p><b>作者：</b>Hellohistory</p><p><b>版本号：</b>v2.0</p><p><b>GitHub：</b><a href='{GITHUB_URL}'>{GITHUB_URL}</a></p><p><b>Gitee：</b><a href='{GITEE_URL}'>{GITEE_URL}</a></p>")

    def _show_thanks(self) -> None:
        QMessageBox.information(self, "感谢",
                                "<h2>特别感谢</h2><p>感谢 <b>经世国学馆 耕田四哥</b>！</p><p>如果没有四哥所制作的 <i>中华甲子历史年表</i>，本项目不可能诞生。</p><p><b>特别声明：</b>本人与经世国学馆无任何关联，仅怀揣学习之心编写此项目。</p>")

    def _build_ui(self) -> None:
        root = QWidget();
        layout = QVBoxLayout(root);
        layout.setContentsMargins(12, 12, 12, 12);
        layout.setSpacing(10)
        form = QHBoxLayout();
        form.setSpacing(8)
        self.year_edit = QLineEdit();
        self.year_edit.setPlaceholderText("公元年份，如 618 或 -841");
        form.addWidget(QLabel("年份："));
        form.addWidget(self.year_edit)
        year_btn = QPushButton("查询年份");
        year_btn.clicked.connect(self._on_search_year);
        form.addWidget(year_btn)
        self.key_edit = QLineEdit();
        self.key_edit.setPlaceholderText("关键字，如 李世民 / 贞观");
        form.addWidget(QLabel("关键字："));
        form.addWidget(self.key_edit)
        key_btn = QPushButton("关键字搜索");
        key_btn.clicked.connect(self._on_search_keyword);
        form.addWidget(key_btn)
        adv_btn = QPushButton("高级搜索…");
        adv_btn.clicked.connect(self._on_advanced_search);
        form.addWidget(adv_btn)
        layout.addLayout(form)
        self.table = self._create_table();
        layout.addWidget(self.table)
        self.setCentralWidget(root)

    def _create_table(self) -> CopyableTableWidget:
        tbl = CopyableTableWidget(columnCount=8);
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers);
        tbl.setHorizontalHeaderLabels(["公元", "干支", "时期", "政权", "帝号", "帝名", "年号", "在位年"]);
        tbl.horizontalHeader().setStretchLastSection(True);
        tbl.horizontalHeader().sectionClicked.connect(self._on_header_clicked);
        tbl.setContextMenuPolicy(Qt.CustomContextMenu);
        tbl.customContextMenuRequested.connect(self._on_table_context_menu);
        return tbl

    def _on_header_clicked(self, section: int) -> None:
        help_map = {0: "公元：公元年份", 1: "干支：甲子历纪年", 2: "时期：朝代", 3: "政权：并立时代划分", 4: "帝号",
                    5: "帝名", 6: "年号", 7: "在位年：年号下的序号"}
        if section in help_map: QToolTip.showText(QCursor.pos(), help_map[section], self)

    def _on_search_year(self) -> None:
        text = self.year_edit.text().strip()
        if not self._is_int(text): self._msg("请输入整数年份"); return
        year = int(text)
        if not (YEAR_MIN <= year <= YEAR_MAX): self._msg(f"仅支持 {YEAR_MIN} ~ {YEAR_MAX} 年"); return
        self._render(self._svc.get_chronology_by_year(year))

    def _on_search_keyword(self) -> None:
        kw = self.key_edit.text().strip()
        if not kw: self._msg("关键字不能为空"); return
        self._render(self._svc.find_entries(kw))

    def _on_advanced_search(self) -> None:
        dlg = AdvancedSearchDialog(self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.get_params()
            self._render(self._svc.advanced_search(**params))

    def _on_table_context_menu(self, pos: QPoint) -> None:
        tbl = self.table;
        menu = QMenu(self)
        copy_sel = QAction("复制所选", self);
        copy_sel.triggered.connect(tbl.copy_selection);
        menu.addAction(copy_sel)
        copy_row = QAction("复制整行", self)

        def _copy_row():
            row = tbl.selectedRanges()[0].topRow()
            texts = [tbl.item(row, c).text() if tbl.item(row, c) else "" for c in range(tbl.columnCount())]
            QApplication.clipboard().setText("\t".join(texts))

        if tbl.selectedRanges(): copy_row.triggered.connect(_copy_row); menu.addAction(copy_row)
        item = tbl.itemAt(pos)
        if item:
            search_val = QAction(f"搜索“{item.text()}”", self)

            def _search_item(): self._render(self._svc.find_entries(item.text()))

            search_val.triggered.connect(_search_item);
            menu.addAction(search_val)
        menu.exec(tbl.mapToGlobal(pos))

    def _render(self, entries: List[HistoryEntry]) -> None:
        if not entries: self._msg("未找到任何匹配记录"); return
        tbl = self.table;
        tbl.setRowCount(len(entries))
        for r, e in enumerate(entries):
            regnal_year_str = str(int(e.regnal_year)) if e.regnal_year is not None else ""
            row = [str(e.year_ad), e.ganzhi or "", e.period or "", e.regime or "", e.emperor_title or "",
                   e.emperor_name or "", e.reign_title or "", regnal_year_str]
            for c, v in enumerate(row): tbl.setItem(r, c, QTableWidgetItem(v))
        tbl.resizeColumnsToContents()

    @staticmethod
    def _is_int(s: str) -> bool:
        return s.lstrip("-").isdigit()

    @staticmethod
    def _msg(text: str) -> None:
        QMessageBox.information(None, "提示", text)
