from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random
from .....utils.impl_obj import VALUE_QUESS, MINES_TAG

def liar_1Xp(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = 1
    if value > 4:
        value = 3
    return value

class Rule1L1Xp(AbstractClueRule):
    name = ["1L1X'", "LX'", "误差 + 小十字", "Liar + Mini Cross"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            nei = pos.neighbors(1)
            value = len([_pos for _pos in nei if board.get_type(_pos) == "F"])
            value = liar_1Xp(value, random)
            board.set_value(pos, Value1L1Xp(pos, code=bytes([value])))
        return board

class Value1L1Xp(AbstractClueValue):
    value: int
    neighbors: list

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = code[0]
        self.neighbors = pos.neighbors(1)
    
    def __repr__(self) -> str:
        return str(self.value)
    
    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors
    
    @classmethod
    def type(cls) -> bytes:
        return Rule1L1Xp.name[0].encode("ascii")
    
    def code(self) -> bytes:
        return bytes([self.value])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        neighbor_vars = board.batch(self.neighbors, mode="variable", drop_none=True)
        neighbor_sum = sum(neighbor_vars)

        b1 = model.NewBoolVar("sum_eq_count_plus_1")
        b2 = model.NewBoolVar("sum_eq_count_minus_1")

        model.Add(neighbor_sum == self.value + 1).OnlyEnforceIf(b1)
        model.Add(neighbor_sum == self.value - 1).OnlyEnforceIf(b2)
        model.AddBoolOr([b1, b2]).OnlyEnforceIf(s)
        model.AddBoolAnd([b1.Not(), b2.Not()]).OnlyEnforceIf(s.Not())
