from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random

def liar_2Xp(vals: [int, int], random) -> int:
    if vals[0] > vals[1]:
        vals[0], vals[1] = vals[1], vals[0]
    # 1/4 chance to choose the smaller one
    val = vals[0 if random.random() < 0.25 else 1]
    val += 1 if random.random() > 0.5 else -1
    if val < 0:
        val = 1
    if val > 4:
        val = 3
    return val

class Rule1L2Xp(AbstractClueRule):
    name = ["1L2X'", "误差 + 十字'", "Liar + Cross'"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            value1 = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F" and board.get_dyed(_pos)])
            value2 = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F" and not board.get_dyed(_pos)])
            value = liar_2Xp([value1, value2], random)
            board.set_value(pos, Value1L2Xp(pos, code=bytes([value])))
        return board

class Value1L2Xp(AbstractClueValue):
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
        return Rule1L2Xp.name[0].encode("ascii")
    
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

        b1 = model.NewBoolVar("vars_a_eq_minus_1")
        b2 = model.NewBoolVar("vars_a_eq_plus_1")
        b3 = model.NewBoolVar("vars_b_eq_minus_1")
        b4 = model.NewBoolVar("vars_b_eq_plus_1")

        model.Add(sum_a == self.value - 1).OnlyEnforceIf(b1)
        model.Add(sum_a == self.value + 1).OnlyEnforceIf(b2)
        model.Add(sum_b == self.value - 1).OnlyEnforceIf(b3)
        model.Add(sum_b == self.value + 1).OnlyEnforceIf(b4)

        model.AddBoolOr([b1, b2, b3, b4]).OnlyEnforceIf(s)
