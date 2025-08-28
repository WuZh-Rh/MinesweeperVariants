"""
[2Q'] 章鱼 (Octopus)：线索表示八方向上最近的2格有雷的方向数量。
"""

from typing import List

from minesweepervariants.utils.impl_obj import MINES_TAG, VALUE_QUESS
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.tool import get_logger

def pos_shift(
        board: AbstractBoard,
        pos: AbstractPosition,
        index: int
):
    shift = [
        (1, 1), (1, 0), (1, -1),
        (0, 1), (0, -1),
        (-1, 1), (-1, 0), (-1, -1)
    ][index]
    positions = []
    for _ in range(2):
        if board.is_valid(_pos := pos.shift(shift[0], shift[1])):
            positions.append(_pos)
            shift = (
                0 if shift[0] == 0 else (shift[0] + 1 if shift[0] > 0 else shift[0] - 1),
                0 if shift[1] == 0 else (shift[1] + 1 if shift[1] > 0 else shift[1] - 1),
            )
    return positions

class Rule2QPrime(AbstractClueRule):
    name = ["2Q'", "章鱼", "Octopus"]
    doc = "线索表示八方向上最近的2格有雷的方向数量"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        for pos, _ in board("N"):
            value = 0
            for i in range(8):
                if "F" in board.batch(pos_shift(board, pos, i), mode="type"):
                    value += 1
            board.set_value(pos, Value2QPrime(pos, count=value))
        return board

class Value2QPrime(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            self.count = code[0]
        else:
            self.count = count
        self.neighbor = None

    def __repr__(self):
        return str(self.count)

    def high_light(self, board: 'AbstractBoard') -> List['AbstractPosition'] | None:
        positions = []

        for i in range(8):
            pos_list = pos_shift(board, self.pos, i)
            type_list = board.batch(pos_list, mode="type")
            if "F" in type_list:
                positions.append(pos_list[type_list.index("F")])
            else:
                positions.extend(pos_list)

        return positions

    @classmethod
    def type(cls) -> bytes:
        return Rule2QPrime.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self.pos)

        tmp_vars = []
        for index in range(8):
            tmp = model.NewBoolVar("tmp")
            var_list = board.batch(pos_shift(board, self.pos, index), mode="variable")
            model.AddBoolOr(var_list).OnlyEnforceIf(tmp)
            model.Add(sum(var_list) == 0).OnlyEnforceIf(tmp.Not())
            tmp_vars.append(tmp)
        model.Add(sum(tmp_vars) == self.count).OnlyEnforceIf(s)
