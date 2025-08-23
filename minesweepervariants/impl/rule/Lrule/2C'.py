#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/07 17:42
# @Author  : Wu_RH
# @FileName: 2C.py
"""
[2C'] 连方' (Connected)：(1) 所有四连通雷区域为 1xn 或 nx1 的矩形；(2) 所有雷区域对角相邻
"""
from typing import List

from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition
from .connect import connect


def block(a_pos: AbstractPosition, board: AbstractBoard) -> List[AbstractPosition]:
    b_pos = a_pos.up()
    c_pos = a_pos.left()
    d_pos = b_pos.left()
    if not board.in_bounds(d_pos):
        return []
    return [a_pos, b_pos, c_pos, d_pos]


class Rule2C(AbstractMinesRule):
    name = ["2C'", "连方'", "Connected"]
    doc = "(1) 所有四连通雷区域为 1xn 或 nx1 的矩形；(2) 所有雷区域对角相邻"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s1 = switch.get(model, self)
        s2 = switch.get(model, self)
        for pos, _ in board():
            var_list = board.batch(block(pos, board), mode="variable")
            if not var_list:
                continue
            model.Add(sum(var_list) <= 2).OnlyEnforceIf(s1)
        connect(
            model,
            board,
            s2
        )
