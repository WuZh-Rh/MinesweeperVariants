#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/15 12:46
# @Author  : Wu_RH
# @FileName: 1B''.py
"""
[1B'']后平衡: 雷处于的行, 列, 斜线的总数为指定值
[1B'']后平衡: 雷八方向上的总雷数均相等
"""

from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition


def get_line(board: AbstractBoard, pos: AbstractPosition):
    result = []
    for move in range(4):
        _pos = pos.clone()
        while True:
            match move:
                case 0:
                    _pos = _pos.up()
                case 1:
                    _pos = _pos.up().left()
                case 2:
                    _pos = _pos.up().right()
                case 3:
                    _pos = _pos.left()
            if not board.in_bounds(_pos):
                break
            result.append(_pos)
        _pos = pos.clone()
        while True:
            match move:
                case 0:
                    _pos = _pos.down()
                case 1:
                    _pos = _pos.down().right()
                case 2:
                    _pos = _pos.down().left()
                case 3:
                    _pos = _pos.right()
            if not board.in_bounds(_pos):
                break
            result.append(_pos)
    return result


class Rule1Bpp(AbstractMinesRule):
    name = ["1B''", "后平衡"]
    doc = "雷八方向上的总雷数均相等"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        if data:
            self.value = int(data)
        else:
            self.value = -1

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        ub = board.boundary().x * 3
        if self.value == -1:
            all_n = model.NewIntVar(0, ub, "[1B'']n_number")
        else:
            all_n = self.value

        for pos, var in board(mode="variable"):
            all_pos = get_line(board, pos)
            all_var = board.batch(all_pos, mode="variable")
            model.Add(sum(all_var) == all_n).OnlyEnforceIf([var, s])
