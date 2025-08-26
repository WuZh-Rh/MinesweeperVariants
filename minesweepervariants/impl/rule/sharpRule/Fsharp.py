#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/23 23:52
# @Author  : Wu_RH
# @FileName: Fshape.py

from minesweepervariants.abs.board import AbstractBoard
from . import AbstractMinesSharp


class RuleFsharp(AbstractMinesSharp):
    name = ["F#", "标签"]
    doc = "包含以下规则:[*3T], [3], [3F]"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        rules_name = ["*3T", "3", "3F"]
        super().__init__(rules_name, board, data)
