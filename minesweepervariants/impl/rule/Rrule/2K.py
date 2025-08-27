"""
[2K] 金将 (Kinsho)：线索表示金将范围（即上、下、左、右、左上、右上六格）内的雷数
"""

from minesweepervariants.utils.impl_obj import MINES_TAG, VALUE_QUESS
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.tool import get_logger

class Rule2K(AbstractClueRule):
    name = ["2K", "金将", "Kinsho"]
    doc = "线索表示金将范围（即上、下、左、右、左上、右上六格）内的雷数"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            neighbors = self.get_kinsho_neighbors(pos, board)
            mine_count = sum(1 for n in neighbors if board.get_type(n) == "F")
            board.set_value(pos, Value2K(pos, count=mine_count))
        return board

    @staticmethod
    def get_kinsho_neighbors(pos: AbstractPosition, board: AbstractBoard):
        x, y = pos.x, pos.y
        board_key = pos.board_key
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, 1), (-1, -1)]
        neighbors = []
        for dx, dy in directions:
            npos = type(pos)(x + dx, y + dy, board_key)
            if board.in_bounds(npos):
                neighbors.append(npos)
        return neighbors

class Value2K(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            self.count = code[0]
        else:
            self.count = count

    def __repr__(self):
        return str(self.count)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return Rule2K.get_kinsho_neighbors(self.pos, board)

    @classmethod
    def type(cls) -> bytes:
        return b'2K'

    def code(self) -> bytes:
        return bytes([self.count])
    
    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        type_dict = {"N": [], "F": []}
        for pos in self.high_light(board):
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
        for neighbor in self.high_light(board):
            var = board.get_variable(neighbor)
            if var is not None:
                neighbor_vars.append(var)
        if neighbor_vars:
            model.Add(sum(neighbor_vars) == self.count).OnlyEnforceIf(s)
            get_logger().trace(f"[2K] {self.pos}: {self.count} constraint: {[str(n) for n in neighbor_vars]} == {self.count}")
