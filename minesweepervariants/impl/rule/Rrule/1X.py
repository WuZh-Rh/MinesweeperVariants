#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/07 18:26
# @Author  : Wu_RH
# @FileName: 1X.py
"""
[1X] 十字 (Cross)：线索表示半径为 2 的十字范围内的雷数
"""
from minesweepervariants.impl.summon.solver import Switch
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition

from ....utils.impl_obj import VALUE_QUESS, MINES_TAG


class Rule1X(AbstractClueRule):
    name = ["1X", "十字", "Cross"]
    doc = "线索表示半径为 2 的十字范围内的雷数"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        self.nei_values = []
        if data is None:
            self.nei_values = [tuple([1, 1]), tuple([4, 4])]
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

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        for pos, _ in board("N"):
            value = len([_pos for _pos in self.nei_pos(pos) if board.get_type(_pos) == "F"])
            obj = Value1X(pos, count=value)
            obj.neighbor = self.nei_pos(pos)
            board.set_value(pos, obj)
        return board

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        for pos, obj in board():
            if not isinstance(obj, Value1X):
                continue
            obj.neighbor = self.nei_pos(pos)


class Value1X(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            # 从字节码解码
            self.count = code[0]
        else:
            # 直接初始化
            self.count = count
        self.neighbor = []

    def __repr__(self):
        return f"{self.count}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbor

    @classmethod
    def type(cls) -> bytes:
        return Rule1X.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

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
        """创建CP-SAT约束：周围雷数等于count"""
        model = board.get_model()
        s = switch.get(model, self)

        # 收集周围格子的布尔变量
        neighbor_vars = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                var = board.get_variable(neighbor)
                neighbor_vars.append(var)

        # 添加约束：周围雷数等于count
        if neighbor_vars:
            model.Add(sum(neighbor_vars) == self.count).OnlyEnforceIf(s)
