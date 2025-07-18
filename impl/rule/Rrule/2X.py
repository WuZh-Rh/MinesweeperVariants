#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 
# @Time    : 2025/06/16 09:20
# @Author  : xxx
# @FileName: 2X.py
"""
[2X] 线索代表相邻的8个格子中，染色和非染色格里的雷数(顺序不确定)
"""
from typing import List, Dict

from abs.Rrule import AbstractClueRule, AbstractClueValue
from abs.board import AbstractBoard, AbstractPosition
from utils.image_create import get_text, get_row

from utils.tool import get_logger, get_random
from utils.solver import get_model


def put(pos: 'AbstractPosition', board: 'AbstractBoard'):
    clue = board.get_value(pos)


class Rule2X(AbstractClueRule):
    name = "2X"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        r = get_random()
        for pos, _ in board("N"):
            value1 = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F" and board.get_dyed(_pos)])
            value2 = len(
                [_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F" and not board.get_dyed(_pos)])
            if r.randint(0, 1): value1, value2 = value2, value1
            board.set_value(pos, Value2X(pos, count=value1 * 10 + value2))
            logger.debug(f"Set {pos} to 2X[{value1 * 10 + value2}]")
        return board

    def clue_class(self):
        return Value2X


class Value2X(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            self.count = code[0]
        else:
            self.count = count
        self.neighbor = self.pos.neighbors(2)

    def __repr__(self) -> str:
        return f"{self.count // 10} {self.count % 10}"

    def compose(self, board) -> List[Dict]:
        value = [self.count // 10, self.count % 10]
        value.sort()
        text_a = get_text(str(value[0]))
        text_b = get_text(str(value[1]))
        return [get_row(
            text_a,
            text_b
        )]

    @classmethod
    def type(cls) -> bytes:
        return Rule2X.name.encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

    def create_constraints(self, board: 'AbstractBoard'):
        """创建CP-SAT约束: 周围染色格雷数等于两个染色格的数量"""
        model = get_model()

        # 收集周围格子的布尔变量
        neighbor_vars1 = []
        neighbor_vars2 = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                if board.get_dyed(neighbor):
                    var = board.get_variable(neighbor)
                    neighbor_vars1.append(var)
                else:
                    var = board.get_variable(neighbor)
                    neighbor_vars2.append(var)

        if neighbor_vars1 or neighbor_vars2:
            # 定义变量
            a1 = model.NewBoolVar('a1')
            b1 = model.NewBoolVar('b1')
            c1 = model.NewBoolVar('c1')
            d1 = model.NewBoolVar('d1')
            A_and_B = model.NewBoolVar('A_and_B')
            C_and_D = model.NewBoolVar('C_and_D')
            # 设置A B C D的值
            model.Add(sum(neighbor_vars1) == self.count // 10).OnlyEnforceIf(a1)
            model.Add(sum(neighbor_vars2) == self.count % 10).OnlyEnforceIf(b1)
            model.Add(sum(neighbor_vars1) == self.count % 10).OnlyEnforceIf(c1)
            model.Add(sum(neighbor_vars2) == self.count // 10).OnlyEnforceIf(d1)
            # 实现 A and B
            model.AddBoolAnd([a1, b1]).OnlyEnforceIf(A_and_B)
            # 实现 C and D
            model.AddBoolAnd([c1, d1]).OnlyEnforceIf(C_and_D)
            # 添加最终值
            model.AddBoolOr([A_and_B, C_and_D])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        return False

    def check(self, board: 'AbstractBoard') -> bool:
        return False

    @classmethod
    def method_choose(cls) -> int:
        return 3
