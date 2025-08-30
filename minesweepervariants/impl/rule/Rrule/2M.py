#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 11:07
# @Author  : xxx
# @FileName: 1L.py
"""
[2M]取模:线索与周围8格的雷数除以3的余数相同
"""

from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition

from ....utils.tool import get_logger


class Rule2M(AbstractClueRule):
    name = ["2M", "取模", "Modulo"]
    doc = "线索与周围8格的雷数除以3的余数相同"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            value = len([_pos for _pos in pos.neighbors(2)
                         if board.get_type(_pos) == "F"]) % 3
            board.set_value(pos, Value2M(pos, count=value))
            logger.debug(f"Set {pos} to 2M[{value}]")
        return board


class Value2M(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            # 从字节码解码
            self.count = code[0]
        else:
            # 直接初始化
            self.count = count
        self.neighbor = self.pos.neighbors(2)

    def __repr__(self):
        return f"{self.count}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbor

    @classmethod
    def type(cls) -> bytes:
        return Rule2M.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

    def create_constraints(self, board: 'AbstractBoard', switch):
        """创建CP-SAT约束：周围雷数等于count"""
        model = board.get_model()
        s = switch.get(model, self)

        # 收集周围格子的布尔变量
        neighbor_vars = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                var = board.get_variable(neighbor)
                neighbor_vars.append(var)

        # 添加约束：周围雷数等于count+-1
        if neighbor_vars:
            neighbor_sum = sum(neighbor_vars)

            b1 = model.NewBoolVar(f"[2M]b1")
            b2 = model.NewBoolVar(f"[2M]b2")
            b3 = model.NewBoolVar(f"[2M]b3")

            # 将布尔变量与表达式绑定
            model.Add(neighbor_sum == self.count).OnlyEnforceIf([b1, s])
            model.Add(neighbor_sum != self.count).OnlyEnforceIf([b1.Not(), s])

            model.Add(neighbor_sum == self.count + 3).OnlyEnforceIf([b2, s])
            model.Add(neighbor_sum != self.count + 3).OnlyEnforceIf([b2.Not(), s])

            model.Add(neighbor_sum == self.count + 6).OnlyEnforceIf([b3, s])
            model.Add(neighbor_sum != self.count + 6).OnlyEnforceIf([b3.Not(), s])

            model.AddBoolOr([b1, b2, b3]).OnlyEnforceIf(s)
