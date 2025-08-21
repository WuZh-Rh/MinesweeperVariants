#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/03 05:26
# @Author  : Wu_RH
# @FileName: V.py
"""
[V]标准扫雷：每个数字标明周围八格内雷的数量。
"""
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition

from ....utils.tool import get_logger
from ....utils.impl_obj import VALUE_QUESS, MINES_TAG


from ....utils.image_create import get_image, get_text, get_row, get_col, get_dummy

from ....utils.web_template import Number

class RuleV(AbstractClueRule):
    name = ["V", "标准扫雷", "Vanlia"]
    doc = "每个数字标明周围八格内雷的数量。"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            value = board.batch(pos.neighbors(2), "type").count("F")
            board.set_value(pos, ValueV(pos, count=value))
            logger.debug(f"Set {pos} to V[{value}]")
        return board


class ValueV(AbstractClueValue):
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
        return b'V'

    def code(self) -> bytes:
        return bytes([self.count])

    def invalid(self, board: 'AbstractBoard') -> bool:
        return board.batch(self.neighbor, mode="type").count("N") == 0

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        type_dict = {"N": [], "F": []}
        for pos in self.neighbor:
            t = board.get_type(pos)
            if t in ("", "C"):
                continue
            type_dict[t].append(pos)
        n_num = len(type_dict["N"])
        f_num = len(type_dict["F"])
        if n_num == 0:
            return False
        if f_num == self.count:
            for i in type_dict["N"]:
                board.set_value(i, VALUE_QUESS)
            return True
        if f_num + n_num == self.count:
            for i in type_dict["N"]:
                board.set_value(i, MINES_TAG)
            return True
        return False

    def create_constraints(self, board: 'AbstractBoard', switch):
        """创建CP-SAT约束: 周围雷数等于count"""
        model = board.get_model()

        # 收集周围格子的布尔变量
        neighbor_vars = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                var = board.get_variable(neighbor)
                neighbor_vars.append(var)

        # 添加约束：周围雷数等于count
        if neighbor_vars:
            model.Add(sum(neighbor_vars) == self.count).OnlyEnforceIf(switch.get(model, self.pos))
            get_logger().trace(f"[V] Value[{self.pos}: {self.count}] add: {neighbor_vars} == {self.count}")

    def web_component(self, board):
        return Number(self.count)