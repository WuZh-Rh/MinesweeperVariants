from typing import List

from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random

def liar_1N(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = -value
    if value > 4:
        value = 3
    return value

class Rule1L1N(AbstractClueRule):
    name = ["1L1N", "LN", "误差 + 负雷", "Liar + Negative"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            positions = pos.neighbors(2)
            value = 0
            for t, d in zip(
                    board.batch(positions, "type"),
                    board.batch(positions, "dye")
            ):
                if t != "F":
                    continue
                if d:
                    value += 1
                else:
                    value -= 1
            value = liar_1N(value, random)
            board.set_value(pos, Value1L1N(pos, code=bytes([value])))
        return board

class Value1L1N(AbstractClueValue):
    value: int
    neighbors: list

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = code[0]
        self.neighbors = pos.neighbors(2)

    def __repr__(self) -> str:
        return str(self.value)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors
    
    @classmethod
    def type(cls) -> bytes:
        return Rule1L1N.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        nei_a = [_pos for _pos in self.neighbors if board.get_dyed(_pos)]
        nei_b = [_pos for _pos in self.neighbors if not board.get_dyed(_pos)]

        vars_a = board.batch(nei_a, mode="variable", drop_none=True)
        vars_b = board.batch(nei_b, mode="variable", drop_none=True)

        diff = sum(vars_a) - sum(vars_b)

        max_abs = len(vars_a) + len(vars_b)
        abs_diff = model.NewIntVar(0, max_abs, "abs_diff")

        b1 = model.NewBoolVar("sum_eq_count_plus_1")
        b2 = model.NewBoolVar("sum_eq_count_minus_1")

        model.AddAbsEquality(abs_diff, diff)
        model.Add(abs_diff == self.value + 1).OnlyEnforceIf(b1)
        model.Add(abs_diff == self.value - 1).OnlyEnforceIf(b2)
        model.AddBoolOr([b1, b2]).OnlyEnforceIf(s)
