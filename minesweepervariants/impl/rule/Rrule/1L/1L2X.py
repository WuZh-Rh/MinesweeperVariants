from typing import Dict

from minesweepervariants.utils.web_template import MultiNumber
from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition
from .....utils.image_create import get_text, get_row

from .....utils.tool import get_logger, get_random

def liar_2X(vals: [int, int], random) -> int:
    idx = 1 if random.random() > 0.5 else 0
    pm = 1 if random.random() > 0.5 else -1
    vals[idx] += pm
    if vals[idx] < 0:
        vals[idx] = 1
    if vals[0] > vals[1]:
        vals[0], vals[1] = vals[1], vals[0]
    return vals[0] * 10 + vals[1]

class Rule1L2X(AbstractClueRule):
    name = ["1L2X", "误差 + 十字", "Liar + Cross"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            value1 = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F" and board.get_dyed(_pos)])
            value2 = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F" and not board.get_dyed(_pos)])
            value = liar_2X([value1, value2], random)
            board.set_value(pos, Value1L2X(pos, code=bytes([value])))
        return board

class Value1L2X(AbstractClueValue):
    value: int
    neighbors: list

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = code[0]
        self.neighbors = pos.neighbors(2)
    
    def __repr__(self) -> str:
        return f"{self.value // 10} {self.value % 10}"
    
    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors
    
    def web_component(self, board) -> Dict:
        value = [self.value // 10, self.value % 10]
        value.sort()
        return MultiNumber(value)

    def compose(self, board) -> Dict:
        value = [self.value // 10, self.value % 10]
        value.sort()
        text_a = get_text(str(value[0]))
        text_b = get_text(str(value[1]))
        return get_row(
            text_a,
            text_b
        )
    
    @classmethod
    def type(cls) -> bytes:
        return Rule1L2X.name[0].encode("ascii")
    
    def code(self) -> bytes:
        return bytes([self.value])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        nei_a = [_pos for _pos in self.neighbors if board.get_dyed(_pos)]
        nei_b = [_pos for _pos in self.neighbors if not board.get_dyed(_pos)]

        vars_a = board.batch(nei_a, mode="variable", drop_none=True)
        vars_b = board.batch(nei_b, mode="variable", drop_none=True)
        sum_a = sum(vars_a)
        sum_b = sum(vars_b)
        x1, x2 = self.value // 10, self.value % 10

        b1 = model.NewBoolVar("vars_a_eq_x1_vars_b_eq_x2_plus_1")
        b2 = model.NewBoolVar("vars_a_eq_x1_vars_b_eq_x2_minus_1")
        b3 = model.NewBoolVar("vars_a_eq_x1_plus_1_vars_b_eq_x2")
        b4 = model.NewBoolVar("vars_a_eq_x1_minus_1_vars_b_eq_x2")
        b5 = model.NewBoolVar("vars_a_eq_x2_vars_b_eq_x1_plus_1")
        b6 = model.NewBoolVar("vars_a_eq_x2_vars_b_eq_x1_minus_1")
        b7 = model.NewBoolVar("vars_a_eq_x2_plus_1_vars_b_eq_x1")
        b8 = model.NewBoolVar("vars_a_eq_x2_minus_1_vars_b_eq_x1")

        model.Add(sum_a == x1).OnlyEnforceIf(b1)
        model.Add(sum_b == x2 + 1).OnlyEnforceIf(b1)
        model.Add(sum_a == x1).OnlyEnforceIf(b2)
        model.Add(sum_b == x2 - 1).OnlyEnforceIf(b2)
        model.Add(sum_a == x1 + 1).OnlyEnforceIf(b3)
        model.Add(sum_b == x2).OnlyEnforceIf(b3)
        model.Add(sum_a == x1 - 1).OnlyEnforceIf(b4)
        model.Add(sum_b == x2).OnlyEnforceIf(b4)
        model.Add(sum_a == x2).OnlyEnforceIf(b5)
        model.Add(sum_b == x1 + 1).OnlyEnforceIf(b5)
        model.Add(sum_a == x2).OnlyEnforceIf(b6)
        model.Add(sum_b == x1 - 1).OnlyEnforceIf(b6)
        model.Add(sum_a == x2 + 1).OnlyEnforceIf(b7)
        model.Add(sum_b == x1).OnlyEnforceIf(b7)
        model.Add(sum_a == x2 - 1).OnlyEnforceIf(b8)
        model.Add(sum_b == x1).OnlyEnforceIf(b8)

        model.AddBoolOr([b1, b2, b3, b4, b5, b6, b7, b8]).OnlyEnforceIf(s)
