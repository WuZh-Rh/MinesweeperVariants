from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random
from .....utils.impl_obj import VALUE_QUESS, MINES_TAG

def liar_1L(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    value += 1 if random.random() > 0.5 else -1
    if value < 1:
        value += 2
    if value > 8:
        value -= 2
    return value

class Rule1L1L(AbstractClueRule):
    name = ["1L1L", "LL", "误差 + 误差", "Liar + Liar"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            value = len([_pos for _pos in pos.neighbors(2) if board.get_type(_pos) == "F"])
            value = liar_1L(value, random)
            board.set_value(pos, Value1L1L(pos, code=bytes([value])))
        return board

class Value1L1L(AbstractClueValue):
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
        return Rule1L1L.name[0].encode("ascii")
    
    def code(self) -> bytes:
        return bytes([self.value])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        neighbor_vars = board.batch(self.neighbors, mode="variable", drop_none=True)
        neighbor_sum = sum(neighbor_vars)

        b1 = model.NewBoolVar("sum_eq_count_plus_2")
        b2 = model.NewBoolVar("sum_eq_count_minus_2")
        b3 = model.NewBoolVar("sum_eq_count")

        model.Add(neighbor_sum == self.value + 2).OnlyEnforceIf(b1)
        model.Add(neighbor_sum == self.value - 2).OnlyEnforceIf(b2)
        model.Add(neighbor_sum == self.value).OnlyEnforceIf(b3)
        model.AddBoolOr([b1, b2, b3]).OnlyEnforceIf(s)
