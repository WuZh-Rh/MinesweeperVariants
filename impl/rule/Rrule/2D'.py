#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/19 20:34
# @Author  : Wu_RH
# @FileName: 2D.py
"""
[2D']偏移: 线索表示四方向任意偏移一格为中心的3x3区域内的总雷数
"""
from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition

from utils.tool import get_logger, get_random
from utils.solver import get_model


class Rule2Dp(AbstractClueRule):
    name = "2D'"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        logger = get_logger()
        for pos, _ in board("N"):
            _pos = random.choice([pos.up(1), pos.down(1), pos.right(1), pos.left(1)])
            value = len([__pos for __pos in _pos.neighbors(0, 2) if board.get_type(__pos) == "F"])
            board.set_value(pos, Value2Dp(pos, count=value))
            logger.debug(f"Set {pos} to 2D[{value}]")
        return board

    def clue_class(self):
        return Value2Dp


class Value2Dp(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            # 从字节码解码
            self.count = code[0]
        else:
            # 直接初始化
            self.count = count
        self.neighbors = []
        for _pos in [pos.up(1), pos.down(1), pos.right(1), pos.left(1)]:
            self.neighbors.append(_pos.neighbors(0, 2))

    def __repr__(self):
        return f"{self.count}"

    @classmethod
    def type(cls) -> bytes:
        return Rule2Dp.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        return False

    def create_constraints(self, board: 'AbstractBoard'):
        """创建CP-SAT约束: 周围雷数等于count"""
        model = get_model()

        # 收集周围格子的布尔变量
        neighbors_vars = []
        for neighbor in self.neighbors:  # 8方向相邻格子
            neighbors_vars.append(board.batch(neighbor, mode="variable", drop_none=True))

        # 添加约束：周围雷数等于count
        var_list = []
        for neighbor_vars in neighbors_vars:
            b = model.NewBoolVar("t")
            model.Add(sum(neighbor_vars) == self.count).OnlyEnforceIf(b)
            model.Add(sum(neighbor_vars) != self.count).OnlyEnforceIf(b.Not())
            var_list.append(b)

        model.AddBoolOr(var_list)

    def method_choose(self) -> int:
        return 1
