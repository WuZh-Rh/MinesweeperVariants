#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/07 18:26
# @Author  : Wu_RH
# @FileName: 1X.py
"""
[1X] 十字 (Cross)：线索表示半径为 2 的十字范围内的雷数
"""
from typing import List

from minesweepervariants.impl.summon.solver import Switch
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition

from ....utils.impl_obj import VALUE_QUESS, MINES_TAG


def encode_bools_7bit(bools: list[bool]) -> bytes:
    """
    将布尔列表转换为字节，每7个布尔值转换为1个字节
    参数:
        bool_list: 布尔值列表
    返回:
        bytes: 转换后的字节对象
    """
    if len(bools) == 0:
        return b''
    bools = [False] * (7 - len(bools) % 7) + bools
    byte_array = bytearray()

    # 每7个布尔值处理为一个字节
    for i in range(0, len(bools), 7):
        group = bools[i:i + 7]
        byte_val = 0

        # 将7个布尔值转换为一个字节
        for j, bit in enumerate(group):
            if bit:
                byte_val |= 1 << (6 - j)  # 设置相应的位

        byte_array.append(byte_val)

    return bytes(byte_array)


def decode_bools_7bit(data: bytes) -> list[bool]:
    # 解码所有数据，每个字节转换为7个布尔值
    bools = []
    for byte in data:
        for shift in range(6, -1, -1):
            bit = (byte >> shift) & 1
            bools.append(bool(bit))

    return bools


class Rule1X(AbstractClueRule):
    name = ["1X", "十字", "Cross"]
    doc = "线索表示半径为 2 的十字范围内的雷数"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        if data is None:
            self.neibor_bool = []
            return
        datas = data.split(";")
        nei_values: list[int] = []
        for nei_value in datas:
            if ":" in nei_value:
                nei_values.extend(tuple([
                    i for i in range(
                        int(nei_value.split(":")[0]),
                        int(nei_value.split(":")[1])+1
                    )
                ]))
            else:
                nei_values.append(int(nei_value))
        if not nei_values:
            return
        max_value = max(nei_values)
        self.neibor_bool = [False for _ in range(max_value)]
        for i in nei_values:
            if i == 0:
                continue
            self.neibor_bool[max_value-i] = True

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        code = b'\x00' + encode_bools_7bit(self.neibor_bool)
        for pos, _ in board("N"):
            obj = Value1X(pos, code)
            value = len([_pos for _pos in obj.neighbor if board.get_type(_pos) == "F"])
            obj.value = value
            board.set_value(pos, obj)
        return board


class Value1X(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, code: bytes = None):
        super().__init__(pos, code)
        self.value, self.data = code[0], code[1:]
        if self.data == b'':
            bool_list = [True, False, False, True]
        else:
            data = self.data
            bool_list = decode_bools_7bit(data)
        self.neighbor = []
        print(bool_list)
        for n, b in enumerate(bool_list[::-1]):
            if not b:
                continue
            self.neighbor.extend(self.pos.neighbors(n + 1, n + 1))

    def __repr__(self):
        return f"{self.value}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbor

    @classmethod
    def type(cls) -> bytes:
        return Rule1X.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value]) + self.data

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
        if f_num == self.value:
            for i in type_dict["N"]:
                board.set_value(i, VALUE_QUESS)
            return True
        if f_num + n_num == self.value:
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
            model.Add(sum(neighbor_vars) == self.value).OnlyEnforceIf(s)
