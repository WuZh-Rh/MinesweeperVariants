#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 11:44
# @Author  : xxx
# @FileName: Q1.py

"""
[1Q]无方: 每个2x2区域内都至少有一个雷
"""

from typing import List

from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractPosition, AbstractBoard

def parse(s: str) -> list[tuple[int, int]]:
    result = [(0,0)]
    for part in s.split(";"):
        x = part.count("R") - part.count("L")
        y = part.count("U") - part.count("D")
        result.append((x, y))
    return result

def block(a_pos: AbstractPosition, offsets: list[tuple[int, int]], board: AbstractBoard) -> List[AbstractPosition]:
    positions = []
    for offset in offsets:
        new_pos = a_pos.shift(offset[1], offset[0])  # 注意这里行列顺序
        if not board.in_bounds(new_pos):
            return []
        positions.append(new_pos)
    return positions


class Rule1Q(AbstractMinesRule):
    name = ["1Q", "Q", "无方"]
    doc = "每个2x2区域内都至少有一个雷"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        self.nei_values = []
        self.rule_name = self.name[0]
        if data is None:
            self.nei_values = [(0,0), (1,0), (0,1), (1,1)]
            return

        self.nei_values = parse(data)
        print(self.nei_values)
        self.rule_name += "(" + data + ")"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        for key in board.get_interactive_keys():
            a_pos = board.boundary(key=key)
            for b_pos in board.get_col_pos(a_pos):
                for i_pos in board.get_row_pos(b_pos):
                    if not (pos_block := block(i_pos, self.nei_values, board)):
                        continue
                    var_list = [board.get_variable(pos) for pos in pos_block]
                    model.AddBoolOr(var_list).OnlyEnforceIf(s)
