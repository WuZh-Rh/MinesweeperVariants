from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random
from .....utils.impl_obj import VALUE_QUESS, MINES_TAG

def liar_1K(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = 1
    if value > 8:
        value = 7
    return value

class Rule1L1K(AbstractClueRule):
    name = ["1L1K", "LK", "误差 + 骑士", "Liar + Knight"]
    doc = ""

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        random = get_random()
        for pos, _ in board("N"):
            nei = pos.neighbors(5, 5)
            value = len([_pos for _pos in nei if board.get_type(_pos) == "F"])
            value = liar_1K(value, random)
            board.set_value(pos, Value1L1K(pos, code=bytes([value])))
        return board

class Value1L1K(AbstractClueValue):
    value: int
    neighbors: list

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = code[0]
        self.neighbors = pos.neighbors(5, 5)
    
    def __repr__(self) -> str:
        return str(self.value)
    
    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors
    
    @classmethod
    def type(cls) -> bytes:
        return Rule1L1K.name[0].encode("ascii")
    
    def code(self) -> bytes:
        return bytes([self.value])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        type_dict = {"N": [], "F": []}
        for pos in self.neighbors:
            t = board.get_type(pos)
            if t in ("", "C"):
                continue
            type_dict[t].append(pos)
        n_num, f_num = len(type_dict["N"]), len(type_dict["F"])
        if n_num == 0:
            return False
        if f_num == self.value + 1:
            for i in type_dict["N"]:
                board.set_value(i, VALUE_QUESS)
            return True
        if n_num + f_num == self.value - 1:
            for i in type_dict["N"]:
                board.set_value(i, MINES_TAG)
            return True
        return False

    
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
