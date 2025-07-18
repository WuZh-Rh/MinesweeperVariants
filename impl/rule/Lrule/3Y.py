#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/18 14:01
# @Author  : Wu_RH
# @FileName: 3I.py
"""
[3Y]阴阳(Yin-Yang):所有雷四连通，所有非雷四连通，不存在2*2的雷或非雷
"""
from typing import List

from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard, AbstractPosition
from impl.rule.Lrule.connect import connect
from utils.impl_obj import get_total
from utils.solver import get_model


def block(a_pos: AbstractPosition, board: AbstractBoard) -> List[AbstractPosition]:
    b_pos = a_pos.up()
    c_pos = a_pos.left()
    d_pos = b_pos.left()
    if not board.in_bounds(d_pos):
        return []
    return [a_pos, b_pos, c_pos, d_pos]


class Rule3Y(AbstractMinesRule):
    name = "3Y"

    @classmethod
    def method_choose(cls) -> int:
        return 1

    def create_constraints(self, board: 'AbstractBoard'):
        model = get_model()

        positions_vars = [(pos, var) for pos, var in board("always", mode="variable")]

        connect(
            model,
            board,
            ub=(len(positions_vars) - get_total()) // 2 + 1,
            connect_value=0,
            nei_value=1
        )
        connect(
            model,
            board,
            ub=get_total() // 2 + 1,
            connect_value=1,
            nei_value=1
        )

        # 大定式
        for pos, _ in board():
            pos_list = block(pos, board)
            if not pos_list:
                continue
            a, b, c, d = board.batch(pos_list, mode="variable")
            model.AddBoolOr([a.Not(), b, c, d.Not()])  # 排除 1010
            model.AddBoolOr([a, b.Not(), c.Not(), d])  # 排除 0101
            model.AddBoolOr([a, b, c, d])  # 排除 0000
            model.AddBoolOr([a.Not(), b.Not(), c.Not(), d.Not()])  # 排除 1111

    def suggest_total(self, info: dict):
        ub = 0
        for key in info["interactive"]:
            size = info["size"][key]
            ub += size[0] * size[1]
        info["soft_fn"](ub * 0.5, 0)
