#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/20 14:12
# @Author  : Wu_RH
# @FileName: 2#.py
"""
[1#']包含以下规则:
[V], [1M], [1L], [1W], [1N], [1X], [1P], [1E], [1X'], [1K], [1W'], [1E'], [1L1M], [1M1N], [1M1X], [1N1X]
"""
from minesweepervariants.abs.board import AbstractBoard
from . import AbstractClueSharp


class Rule1sharp(AbstractClueSharp):
    name = ["1#'", "标签"]
    doc = ("包含以下规则:[V], [1M], [1L], [1W], [1N], [1X], [1P], [1E], "
           "[1X'], [1K], [1W'], [1E'], [1L1M], [1M1N], [1M1X], [1N1X]")

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        rules_name = ["V", "1M", "1L", "1W", "1N", "1X", "1P", "1E", "1X'", "1K", "1W'", "1E'", "1L1M", "1M1N", "1M1X", "1N1X"]
        super().__init__(rules_name, board, data)

