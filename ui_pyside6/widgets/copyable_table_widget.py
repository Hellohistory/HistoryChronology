# ui_pyside6/widgets/copyable_table_widget.py
# -*- coding: utf-8 -*-
"""
扩展 QTableWidget：支持框选复制（Ctrl+C）
"""

from __future__ import annotations

from typing import List

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QTableWidget,
    QTableWidgetItem,
)


class CopyableTableWidget(QTableWidget):
    """按 Ctrl+C 复制选中区域为 TSV 文本"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 支持多选
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        # 绑定 Ctrl+C 快捷键（与 PySide2 版一致）
        QShortcut(QKeySequence.Copy, self, activated=self.copy_selection)

    def copy_selection(self) -> None:
        """把当前选区内容复制到剪贴板，格式为制表符分隔"""
        sel = self.selectedRanges()
        if not sel:
            return
        rng = sel[0]
        rows = range(rng.topRow(), rng.bottomRow() + 1)
        cols = range(rng.leftColumn(), rng.rightColumn() + 1)

        lines: List[str] = []
        for r in rows:
            cells: List[str] = []
            for c in cols:
                item = self.item(r, c)
                cells.append("" if item is None else item.text())
            lines.append("\t".join(cells))

        QApplication.clipboard().setText("\n".join(lines))

    @staticmethod
    def createItem(text: str) -> QTableWidgetItem:
        """统一创建单元格 Item"""
        return QTableWidgetItem(text)
