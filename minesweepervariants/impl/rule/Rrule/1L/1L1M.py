"""
[1L1M] 误差 + 多雷
"""

from typing import List

from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random

def liar_1M(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = 1
    if value > 12:
        value = 11
    return value

class Rule1L1M(AbstractClueRule):
    name = ["1L1M", "LM", "误差 + 多雷", "Liar + Multiple"]
    doc = ""
    
    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        logger = get_logger()
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
                    value += 2
                else:
                    value += 1
            value = liar_1M(value, random)
            board.set_value(pos, Value1L1M(pos, code=bytes([value])))
            logger.debug(f"[1L1M]: put {value} to {pos}")
        return board
    
class Value1L1M(AbstractClueValue):
    value: int
    neighbors: list

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = code[0]
        self.neighbors = pos.neighbors(2)

    def __repr__(self) -> str:
        return f"{self.value}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors
    
    @classmethod
    def type(cls) -> bytes:
        return Rule1L1M.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        vals = []
        offset = 0
        dyes = board.batch(self.neighbors, "dye")
        for pos, dye in zip(self.neighbors, dyes):
            if board.get_type(pos) == "C":
                continue
            if board.get_type(pos) == "F":
                offset += 2 if dye else 1
                continue
            if not board.in_bounds(pos):
                continue
            if dye:
                vals.append(board.get_variable(pos) * 2)
            else:
                vals.append(board.get_variable(pos))
        if vals:
            neighbor_sum = sum(vals)
            b1 = model.NewBoolVar("sum_eq_count_plus_1")
            b2 = model.NewBoolVar("sum_eq_count_minus_1")
            remaining = self.value - offset

            model.Add(neighbor_sum == remaining + 1).OnlyEnforceIf(b1)
            # model.Add(neighbor_sum != remaining + 1).OnlyEnforceIf(b1.Not())
            model.Add(neighbor_sum == remaining - 1).OnlyEnforceIf(b2)
            # model.Add(neighbor_sum != remaining - 1).OnlyEnforceIf(b2.Not())

            model.AddBoolOr([b1, b2]).OnlyEnforceIf(s)
