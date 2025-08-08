# core/data/repository.py
# -*- coding: utf-8 -*-
"""
数据访问层：封装 SQLite 查询，支持简繁体混合检索（基于 OpenCC 纯 Python 实现）
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

from opencc import OpenCC
from core.models.history_entry import HistoryEntry


class ChronologyRepository:
    """负责所有数据库读取操作，支持简繁体互转查询"""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        self._conn.row_factory = sqlite3.Row
        # 预创建 OpenCC 转换器，避免在热路径频繁构造
        self._cc_s2t = OpenCC("s2t")  # 简 → 繁
        self._cc_t2s = OpenCC("t2s")  # 繁 → 简

    @staticmethod
    def _rows_to_entries(rows: Iterable[sqlite3.Row]) -> List[HistoryEntry]:
        out: List[HistoryEntry] = []
        for row in rows:
            period = row["时期"] if "时期" in row.keys() else ""
            regime = row["政权"] if "政权" in row.keys() else ""
            out.append(HistoryEntry(
                year_ad=row["公元"],
                ganzhi=row["干支"],
                period=period,
                regime=regime,
                emperor_title=row["帝号"],
                emperor_name=row["帝名"],
                reign_title=row["年号"],
                regnal_year=row["年份"],
            ))
        return out

    def _generate_variants(self, text: str) -> Set[str]:
        """
        使用 OpenCC 生成简体/繁体变体。
        如需更激进的召回，可追加 s2tw / s2hk 的转换结果。
        """
        variants: Set[str] = {text}
        try:
            variants.add(self._cc_s2t.convert(text))  # 简 → 繁
            variants.add(self._cc_t2s.convert(text))  # 繁 → 简
        except Exception:
            # 转换失败不影响查询流程
            pass
        return variants

    def _split_keyword(self, keyword: str) -> List[str]:
        mapping = {
            "東周（春秋）": ["東周", "春秋"], "东周（春秋）": ["东周", "春秋"],
            "東周（戰國）": ["東周", "戰國"], "东周（战国）": ["东周", "战国"],
        }
        return mapping.get(keyword, [keyword])

    def get_entries_by_year(self, year: int) -> List[HistoryEntry]:
        cur = self._conn.execute(
            "SELECT * FROM history_chronology WHERE 公元 = ? ORDER BY 年份",
            (year,),
        )
        return self._rows_to_entries(cur.fetchall())

    def search_entries(self, keyword: str) -> List[HistoryEntry]:
        keywords = self._split_keyword(keyword)
        all_results: List[HistoryEntry] = []
        seen_keys: Set[Tuple[int, str, str, str]] = set()

        for key in keywords:
            variants = self._generate_variants(key)
            text_cols = ["干支", "帝号", "帝名", "年号", "时期", "政权"]
            conditions: List[str] = []
            params: List[str] = []
            for var in variants:
                like = f"%{var}%"
                for col in text_cols:
                    conditions.append(f"{col} LIKE ?")
                    params.append(like)
            where_sql = " OR ".join(conditions)
            sql = f"SELECT * FROM history_chronology WHERE {where_sql} ORDER BY 公元, 年份"
            cur = self._conn.execute(sql, tuple(params))
            results = self._rows_to_entries(cur.fetchall())

            for entry in results:
                unique_key = (entry.year_ad, entry.ganzhi, entry.emperor_title, entry.reign_title)
                if unique_key not in seen_keys:
                    seen_keys.add(unique_key)
                    all_results.append(entry)

        return all_results

    def advanced_query(
        self,
        *,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        ganzhi: str | None = None,
        period: str | None = None,
        regime: str | None = None,
        emperor_title: str | None = None,
        emperor_name: str | None = None,
        reign_title: str | None = None,
    ) -> List[HistoryEntry]:
        conditions: List[str] = []
        params: List[object] = []

        if year_from is not None:
            conditions.append("公元 >= ?")
            params.append(year_from)
        if year_to is not None:
            conditions.append("公元 <= ?")
            params.append(year_to)

        def add_text_condition(col: str, val: str) -> None:
            keys = self._split_keyword(val)
            col_conds: List[str] = []
            for key in keys:
                for variant in self._generate_variants(key):
                    col_conds.append(f"{col} LIKE ?")
                    params.append(f"%{variant}%")
            if col_conds:
                conditions.append(f"({' OR '.join(col_conds)})")

        if ganzhi:
            add_text_condition("干支", ganzhi)
        if period:
            add_text_condition("时期", period)
        if regime:
            add_text_condition("政权", regime)
        if emperor_title:
            add_text_condition("帝号", emperor_title)
        if emperor_name:
            add_text_condition("帝名", emperor_name)
        if reign_title:
            add_text_condition("年号", reign_title)

        where_sql = " AND ".join(conditions) if conditions else "1"
        sql = f"SELECT * FROM history_chronology WHERE {where_sql} ORDER BY 公元, 年份"
        cur = self._conn.execute(sql, tuple(params))
        return self._rows_to_entries(cur.fetchall())

    def close(self) -> None:
        self._conn.close()
