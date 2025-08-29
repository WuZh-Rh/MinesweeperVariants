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


class Rule3Y(AbstractMinesRule):
    name = ["3Y", "阴阳", "Yin-Yang"]
    doc = "所有雷四连通，所有非雷四连通，不存在2*2的雷或非雷"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        positions_vars = [(pos, var) for pos, var in board("always", mode="variable")]

        connect(
            model,
            board,
            ub=len(positions_vars),
            connect_value=0,
            nei_value=1,
            switch=s
        )
        connect(
            model,
            board,
            ub=len(positions_vars),
            connect_value=1,
            nei_value=1,
            switch=s
        )

        # 大定式
        for pos, _ in board():
            pos_list = block(pos, board)
            if not pos_list:
                continue
            vars = [board.get_variable(p) for p in pos_list if board.in_bounds(p)]
            # model.AddBoolOr([a.Not(), b, c, d.Not()]).OnlyEnforceIf(s)  # 排除 1010
            # model.AddBoolOr([a, b.Not(), c.Not(), d]).OnlyEnforceIf(s)  # 排除 0101
            model.AddBoolOr(vars).OnlyEnforceIf(s)  # 排除 0000
            model.AddBoolOr([v.Not() for v in vars]).OnlyEnforceIf(s)  # 排除 1111

    def suggest_total(self, info: dict):
        ub = 0
        for key in info["interactive"]:
            size = info["size"][key]
            ub += size[0] * size[1]
        info["soft_fn"](ub * 0.5, 0)
