#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/09 03:20
# @Author  : Wu_RH
# @FileName: 2E^.py
"""
[2E^] 加密^ (Encrypted^)：线索被字母替代，每个数字与字母两两对应 [副版规则]
"""

from ....abs.board import AbstractBoard, AbstractPosition
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....utils.impl_obj import VALUE_QUESS, VALUE_CROSS, VALUE_CIRCLE
from ....utils.tool import get_random

NAME_2Eq = "2E^"


class Rule2Eq(AbstractClueRule):
    name = ["2E^", "加密^", "Encrypted^"]

    def __init__(self, data=None, board: 'AbstractBoard' = None):
        super().__init__(board, data)
        pos = board.boundary()
        size = min(pos.x + 1, 9)
        board.generate_board(NAME_2Eq, (size, size))
        board.set_config(NAME_2Eq, "pos_label", True)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        while True:
            shuffled_nums = [i // 2 for i in range(min(18, (board.boundary().x + 1) * 2))]
            number_map = {i: [] for i in range(min(9, (board.boundary().x + 1)))}
            for i in range(min(18, (board.boundary().x + 1) * 2)):
                tmp_list = []
                while shuffled_nums:
                    index = int(random.random() * len(shuffled_nums))
                    if shuffled_nums[index] in number_map[i // 2]:
                        tmp_list.append(shuffled_nums.pop(index))
                        continue
                    number_map[i // 2].append(shuffled_nums.pop(index))
                    break
                if tmp_list:
                    shuffled_nums.extend(tmp_list)
            if not shuffled_nums:
                break

        for pos, _ in board("N"):
            count = board.batch(pos.neighbors(2), mode="type").count("F")
            if count > board.boundary().x:
                board.set_value(pos, VALUE_QUESS)
            else:
                code = bytes([random.choice(number_map[count])])
                board.set_value(pos, Value2Eq(pos, code))

        for x in number_map:
            for y in number_map[x]:
                pos = board.get_pos(x, y, NAME_2Eq)
                board.set_value(pos, VALUE_CIRCLE)

        for pos, _ in board("N", key=NAME_2Eq):
            board.set_value(pos, VALUE_CROSS)

        return board

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        bound = board.boundary(key=NAME_2Eq)

        row = board.get_row_pos(bound)
        for pos in row:
            line = board.get_col_pos(pos)
            var = board.batch(line, mode="variable")
            model.Add(sum(var) == 2).OnlyEnforceIf(s)

        col = board.get_col_pos(bound)
        for pos in col:
            line = board.get_row_pos(pos)
            var = board.batch(line, mode="variable")
            model.Add(sum(var) == 2).OnlyEnforceIf(s)

    def init_clear(self, board: 'AbstractBoard'):
        for pos, _ in board(key=NAME_2Eq):
            board.set_value(pos, None)


class Value2Eq(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.neighbors = pos.neighbors(2)
        self.pos = pos

    def __repr__(self) -> str:
        return "ABCDEFGHI"[self.value]

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors

    @classmethod
    def type(cls) -> bytes:
        return Rule2Eq.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        line = board.batch(board.get_col_pos(
            board.get_pos(0, self.value, NAME_2Eq)
        ), mode="variable")

        neighbors = board.batch(self.neighbors, mode="variable", drop_none=True)

        tmp_vars = []

        for index in range(len(line)):
            tmp_var = model.NewBoolVar("tmp")
            model.Add(sum(neighbors) != index).OnlyEnforceIf([line[index].Not(), s])
            model.Add(sum(neighbors) == index).OnlyEnforceIf([line[index], tmp_var, s])
            tmp_vars.append(tmp_var)

        model.AddBoolOr(tmp_vars).OnlyEnforceIf(s)
