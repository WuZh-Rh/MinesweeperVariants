"""
[2K'] 钻石 (Diamond)：线索表示距离不超过 2 的范围内的雷数
"""

from minesweepervariants.utils.impl_obj import MINES_TAG, VALUE_QUESS
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.tool import get_logger

class Rule2KPrime(AbstractClueRule):
    name = ["2K'", "钻石", "Diamond"]
    doc = "线索表示距离不超过 2 的范围内的雷数"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            neighbors = pos.neighbors(4) # 12 cells at distance 1, √2, 2
            value = sum(1 for n in neighbors if board.get_type(n) == "F")
            board.set_value(pos, Value2KPrime(pos, count=value))
            logger.debug(f"Set {pos} to 2K'[{value}]")
        return board

class Value2KPrime(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            self.count = code[0]
        else:
            self.count = count
        self.neighbor = self.pos.neighbors(4)

    def __repr__(self):
        return f"{self.count}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbor

    @classmethod
    def type(cls) -> bytes:
        return Rule2KPrime.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        type_dict = {"N": [], "F": []}
        for pos in self.neighbor:
            t = board.get_type(pos)
            if t in ("", "C"):
                continue
            type_dict[t].append(pos)
        n_num = len(type_dict["N"])
        f_num = len(type_dict["F"])
        if n_num == 0:
            return False
        if f_num == self.count:
            for i in type_dict["N"]:
                board.set_value(i, VALUE_QUESS)
            return True
        if f_num + n_num == self.count:
            for i in type_dict["N"]:
                board.set_value(i, MINES_TAG)
            return True
        return False
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self.pos)
        neighbor_vars = []
        for neighbor in self.neighbor:
            var = board.get_variable(neighbor)
            if var is not None:
                neighbor_vars.append(var)
        if neighbor_vars:
            model.Add(sum(neighbor_vars) == self.count).OnlyEnforceIf(s)
            get_logger().trace(f"[2K'] {self.pos}: {self.count} constraint: {[str(n) for n in neighbor_vars]} == {self.count}")