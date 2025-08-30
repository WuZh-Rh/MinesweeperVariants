from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random
from .....utils.impl_obj import VALUE_QUESS, MINES_TAG

def liar_2M(value: int, random) -> int:
    value = value % 3
    if value == 0:
        return 1
    elif value == 1:
        return 2 if random.random() > 0.5 else 0
    else:
        return 1

class Rule1L2M(AbstractClueRule):
    name = ["1L2M", "误差 + 取模", "Liar + Modulo"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            nei = pos.neighbors(2)
            value = len([_pos for _pos in nei if board.get_type(_pos) == "F"])
            value = liar_2M(value, random)
            board.set_value(pos, Value1L2M(pos, code=bytes([value])))
        return board

class Value1L2M(AbstractClueValue):
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
        return Rule1L2M.name[0].encode("ascii")
    
    def code(self) -> bytes:
        return bytes([self.value])
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        neighbor_vars = board.batch(self.neighbors, mode="variable", drop_none=True)
        neighbor_sum = sum(neighbor_vars)

        if self.value == 0 or self.value == 2:
            b1 = model.NewBoolVar("[2M]b1")
            b2 = model.NewBoolVar("[2M]b2")
            b3 = model.NewBoolVar("[2M]b3")
            model.Add(neighbor_sum == 1).OnlyEnforceIf(b1)
            model.Add(neighbor_sum == 4).OnlyEnforceIf(b2)
            model.Add(neighbor_sum == 7).OnlyEnforceIf(b3)
            model.AddBoolOr([b1, b2, b3]).OnlyEnforceIf(s)
        else:
            b1 = model.NewBoolVar("[2M]b1")
            b2 = model.NewBoolVar("[2M]b2")
            b3 = model.NewBoolVar("[2M]b3")
            b4 = model.NewBoolVar("[2M]b4")
            b5 = model.NewBoolVar("[2M]b5")
            b6 = model.NewBoolVar("[2M]b6")
            model.Add(neighbor_sum == 0).OnlyEnforceIf(b1)
            model.Add(neighbor_sum == 2).OnlyEnforceIf(b2)
            model.Add(neighbor_sum == 3).OnlyEnforceIf(b3)
            model.Add(neighbor_sum == 5).OnlyEnforceIf(b4)
            model.Add(neighbor_sum == 6).OnlyEnforceIf(b5)
            model.Add(neighbor_sum == 8).OnlyEnforceIf(b6)
            model.AddBoolOr([b1, b2, b3, b4, b5, b6]).OnlyEnforceIf(s)
