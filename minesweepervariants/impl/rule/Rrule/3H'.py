"""
[3H'] 小三角 (Triangle): 线索表示这些周围格子的雷数：左 右，奇数列额外包括上；偶数列额外包括下
"""
from minesweepervariants.utils.impl_obj import MINES_TAG, VALUE_QUESS
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.tool import get_logger

class Rule3H(AbstractClueRule):
    name = ["3H'", "小三角", "Triangle"]
    doc = "线索表示这些周围格子的雷数：左 右，奇数列额外包括上；偶数列额外包括下"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        for pos, _ in board("N"):
            neighbors = self.get_neighbors(pos, board)
            mine_count = sum(1 for n in neighbors if board.get_type(n) == "F")
            board.set_value(pos, Value3H(pos, count=mine_count))
        return board

    @staticmethod
    def get_neighbors(pos: AbstractPosition, board: AbstractBoard):
        x, y = pos.x, pos.y
        board_key = pos.board_key
        directions = [(0, -1), (0, 1)]  # 左右
        if y % 2 == 1:
            directions += [(1, 0)]  # 奇数列 上
        else:
            directions += [(-1, 0)]    # 偶数列 下
        neighbors = []
        for dx, dy in directions:
            npos = type(pos)(x + dx, y + dy, board_key)
            if board.in_bounds(npos):
                neighbors.append(npos)
        return neighbors

class Value3H(AbstractClueValue):
    def __init__(self, pos: AbstractPosition, count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            self.count = code[0]
        else:
            self.count = count

        self.col = (pos.y % 2 == 1)

    def __repr__(self):
        return str(self.count)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return Rule3H.get_neighbors(self.pos, board)

    @classmethod
    def type(cls) -> bytes:
        return b'3H\''

    def code(self) -> bytes:
        return bytes([self.count])


    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        type_dict = {"N": [], "F": []}
        for pos in Rule3H.get_neighbors(self.pos, board):
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
        """创建CP-SAT约束: 邻居雷数等于count"""
        model = board.get_model()
        s = switch.get(model, self.pos)
        neighbor_vars = []
        for neighbor in Rule3H.get_neighbors(self.pos, board):
            var = board.get_variable(neighbor)
            if var is not None:
                neighbor_vars.append(var)
        if neighbor_vars:
            model.Add(sum(neighbor_vars) == self.count).OnlyEnforceIf(s)
