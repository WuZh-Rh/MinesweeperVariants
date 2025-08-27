#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/07 17:13
# @Author  : Wu_RH
# @FileName: 1C.py
"""
[1C] 八连通 (Connected)：雷区域八连通
"""
from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.impl_obj import get_total

from .connect import connect


class Rule1C(AbstractMinesRule):
    name = ["1C", "C", "八连通", "Connected"]
    doc = "雷区域八连通"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        self.nei_values = []
        if data is None:
            self.nei_values = [tuple([1, 2])]
            return
        nei_values = data.split(";")
        for nei_value in nei_values:
            if ":" in nei_value:
                self.nei_values.append(tuple([
                    int(nei_value.split(":")[0]),
                    int(nei_value.split(":")[1])
                ]))
            else:
                self.nei_values.append(tuple([int(nei_value)]))

    def nei_pos(self, pos: AbstractPosition):
        positions = []
        for nei_value in self.nei_values:
            if len(nei_value) == 1:
                positions.extend(
                    pos.neighbors(nei_value[0], nei_value[0])
                )
            elif len(nei_value) == 2:
                positions.extend(
                    pos.neighbors(nei_value[0], nei_value[1])
                )
        return positions

    def create_constraints(self, board, switch):
        model = board.get_model()
        connect(
            model=model,
            board=board,
            connect_value=1,
            nei_value=self.nei_pos,
            switch=switch.get(model, self)
        )
