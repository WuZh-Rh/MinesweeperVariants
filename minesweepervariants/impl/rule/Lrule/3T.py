#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/28 03:49
# @Author  : Wu_RH
# @FileName: 3T.py
"""
[3T]无三连:任意三个雷不能等距排布
"""

from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard


class Rule1T(AbstractMinesRule):
    name = ["3T", "无三连"]
    doc = "任意三个雷不能等距排布"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        for key in board.get_interactive_keys():
            pos_bound = board.boundary(key=key)
            max_num = max(pos_bound.x, pos_bound.y) + 1
            for pos, _ in board():
                positions = []
                for i in range(-(max_num // 2 + 1), max_num // 2 + 1):
                    for j in range(max_num // 2 + 1):
                        if i == 0 and j == 0:
                            continue
                        positions.append([
                            pos, pos.shift(i, j),
                            pos.shift(2*i, 2*j)
                        ])
                for position in positions:
                    var_list = board.batch(position, mode="variable")
                    if True in [i is None for i in var_list]:
                        continue
                    model.Add(sum(var_list) != 3).OnlyEnforceIf(s)
