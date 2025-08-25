#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/15 10:14
# @Author  : Wu_RH
# @FileName: 3W.py
"""
[3W]风云（全称风起云涌）:
传参: 3W:a:b。
其中a只能=1和2，1为风起（每一列的最高的雷的高度不低于它左边一列的最高的雷的高度），2为潮汐（每一列的最高的雷的高度不低于它左边一列的最高的雷的高度，每一列的最低的雷的高度不高于它左边一列的最低的雷的高度）。特殊情况：如果某一列没有雷，那么它左边所有列都没有雷。
其中b只能=1,2,3，1为行失衡，2为列平衡，3为行失衡+列平衡，不填则不加条件。
"""
from minesweepervariants.abs.Lrule import AbstractMinesRule
from minesweepervariants.abs.board import AbstractBoard
from minesweepervariants.impl.summon.solver import Switch


class Rule3W(AbstractMinesRule):
    name = ["3W", "风云"]
    doc = "每行雷数不同，每列中最高的雷的高度不低于它左边一列的最高的雷的高度（特殊情况：如果某一列没有雷，那么它左边所有列都没有雷）。"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        data = "1:0" if data is None else data
        self.a = int(data.split(":")[0])
        if ":" not in data:
            data += ":0"
        self.b = int(data.split(":")[1])

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        model = board.get_model()
        s = switch.get(model, self)

        for key in board.get_interactive_keys():
            pos_bound = board.boundary(key)
            for row_pos in board.get_row_pos(pos_bound):
                if not board.in_bounds(row_pos.left()):
                    continue
                col = board.get_col_pos(row_pos)
                left_col = board.get_col_pos(row_pos.left())
                for col_pos in col:
                    if self.a in [1, 2]:
                        left_pos = col_pos.left()
                        var_list = board.batch(col[:col.index(col_pos)], "var")
                        left_var = board.batch(left_col[:left_col.index(left_pos)], "var")
                        model.AddBoolAnd([v.Not() for v in left_var]).OnlyEnforceIf(
                            [v.Not() for v in var_list] + [board.get_variable(col_pos), s]
                        )
                    if self.a == 2:
                        left_pos = col_pos.left()
                        var_list = board.batch(col[col.index(col_pos)+1:], "var")
                        left_var = board.batch(left_col[left_col.index(left_pos)+1:], "var")
                        model.AddBoolAnd([v.Not() for v in left_var]).OnlyEnforceIf(
                            [v.Not() for v in var_list] + [board.get_variable(col_pos), s]
                        )
                model.AddBoolAnd([v.Not() for v in board.batch(left_col, "var")]).OnlyEnforceIf(
                    [v.Not() for v in board.batch(col, "var")] + [s]
                )
            if self.b & 1:
                col = board.get_col_pos(pos_bound)
                for pos1 in col:
                    for pos2 in col[col.index(pos1)+1:]:
                        row1 = board.get_row_pos(pos1)
                        row2 = board.get_row_pos(pos2)
                        model.Add(sum(board.batch(row1, "var")) != sum(board.batch(row2, "var"))).OnlyEnforceIf(s)
            if self.b & 2:
                row_positions = board.get_row_pos(pos_bound)
                row_sums = [
                    sum(board.get_variable(_pos) for _pos in board.get_col_pos(pos))
                    for pos in row_positions
                ]
                # 所有 row_sums 相等
                for i in range(1, len(row_sums)):
                    model.Add(row_sums[i] == row_sums[0]).OnlyEnforceIf(s)
