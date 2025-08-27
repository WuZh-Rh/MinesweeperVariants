#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/01 07:30
# @Author  : Wu_RH
# @FileName: 2E.py
"""
[2E]加密: 线索被字母所取代，每个字母对应一个线索，且每个线索对应一个字母
"""
from typing import List, Dict

from minesweepervariants.utils.image_create import get_text
from minesweepervariants.utils.web_template import Number
from .....abs.board import AbstractBoard, AbstractPosition
from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....utils.impl_obj import VALUE_QUESS, VALUE_CROSS, VALUE_CIRCLE
from .....utils.tool import get_random

NAME_2E = "2E"


class Rule2E(AbstractClueRule):
    name = ["2E", "加密"]
    doc = "线索被字母所取代，每个字母对应一个线索，且每个线索对应一个字母"

    def __init__(self, data=None, board: 'AbstractBoard' = None):
        super().__init__(board, data)
        pos = board.boundary()
        size = min(pos.x + 1, 9)
        board.generate_board(NAME_2E, (size, size))
        board.set_config(NAME_2E, "pos_label", True)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        shuffled_nums = [i for i in range(min(9, board.boundary().x + 1))]
        random.shuffle(shuffled_nums)
        for pos, _ in board("N"):
            count = board.batch(pos.neighbors(2), mode="type").count("F")
            if count not in shuffled_nums:
                board.set_value(pos, VALUE_QUESS)
            else:
                code = bytes([shuffled_nums[count]])
                board.set_value(pos, Value2E(pos, code))

        for x, y in enumerate(shuffled_nums):
            pos = board.get_pos(x, y, NAME_2E)
            board.set_value(pos, VALUE_CIRCLE)

        for pos, _ in board("N", key=NAME_2E):
            board.set_value(pos, VALUE_CROSS)

        return board

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        bound = board.boundary(key=NAME_2E)

        row = board.get_row_pos(bound)
        for pos in row:
            line = board.get_col_pos(pos)
            var = board.batch(line, mode="variable")
            model.Add(sum(var) == 1).OnlyEnforceIf(s)

        col = board.get_col_pos(bound)
        for pos in col:
            line = board.get_row_pos(pos)
            var = board.batch(line, mode="variable")
            model.Add(sum(var) == 1).OnlyEnforceIf(s)

    def init_clear(self, board: 'AbstractBoard'):
        for pos, _ in board(key=NAME_2E):
            board.set_value(pos, None)


class Value2E(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.pos = pos
        self.neighbors = pos.neighbors(2)

    def __repr__(self) -> str:
        return "ABCDEFGHI"[self.value]

    def web_component(self, board) -> Dict:
        line = board.batch(board.get_col_pos(
            board.get_pos(0, self.value, NAME_2E)
        ), mode="type")
        if "F" in line:
            return Number(line.index("F"))
        return Number("ABCDEFGHI"[self.value])

    def compose(self, board) -> Dict:
        line = board.batch(board.get_col_pos(
            board.get_pos(0, self.value, NAME_2E)
        ), mode="type")
        if "F" in line:
            return get_text(str(line.index("F")))
        return get_text("ABCDEFGHI"[self.value])

    def high_light(self, board: 'AbstractBoard') -> List['AbstractPosition']:
        return self.neighbors

    @classmethod
    def type(cls) -> bytes:
        return Rule2E.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        line = board.batch(board.get_col_pos(
            board.get_pos(0, self.value, NAME_2E)
        ), mode="variable")

        neighbors = board.batch(self.neighbors, mode="variable", drop_none=True)

        for index in range(len(line)):
            model.Add(sum(neighbors) == index).OnlyEnforceIf(line[index]).OnlyEnforceIf(s)
            model.Add(sum(neighbors) != index).OnlyEnforceIf(line[index].Not()).OnlyEnforceIf(s)
