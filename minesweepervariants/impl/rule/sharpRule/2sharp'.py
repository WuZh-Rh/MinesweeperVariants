#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/20 14:12
# @Author  : Wu_RH
# @FileName: 2#.py
"""
[2#]: 包含以下规则:[V], [2X], [2X'], [2D], [2P], [2M], [2A]
注: 通过"2#:"来去除2A
"""
from minesweepervariants.abs.board import AbstractBoard
from . import AbstractClueSharp


class Rule2sharp(AbstractClueSharp):
    name = ["2#'", "标签"]
    doc = "包含以下规则:[V], [2X], [2X'], [2D], [2P], [2M], [2A]"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        rules_name = ["V", "2X", "2X'", "2D", "2P", "2M"]
        if data is None:
            rules_name += ["2A"]
        super().__init__(rules_name, board, data)


