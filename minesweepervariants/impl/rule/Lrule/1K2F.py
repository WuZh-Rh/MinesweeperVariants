#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/27 14:42
# @Author  : mojimoon
# @FileName: 1K2F.py
"""
[1K2F]马步花田: 染色格中的雷的八个马步位置内恰好有1个雷
"""

from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard

class Rule1K2F(AbstractMinesRule):
    name = ["1K2F", "马步花田", "KnightFlower"]
    doc = "染色格中的雷的八个马步位置内恰好有1个雷"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        for pos, dye in board(mode="dye"):
            if not dye:
                continue
            positions = [_pos for _pos in pos.neighbors(5, 5)]
            # sum(vals) 表示马步格内的雷数
            sum_vals = sum(board.batch(positions, mode="variable", drop_none=True))
            val = board.get_variable(pos)
            # val 为1时，vals中必须有且仅有一个1
            # 约束：val=1 => sum(vals) == 1
            model.Add(sum_vals == 1).OnlyEnforceIf([val, s])
