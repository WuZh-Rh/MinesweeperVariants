"""
[2P']旅程: 线索表示距离最近的 2 个雷的曼哈顿距离之和
"""

from ....abs.board import AbstractBoard, AbstractPosition
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....utils.tool import get_logger
from ....utils.impl_obj import VALUE_QUESS, MINES_TAG

def manhattan_neighbors(pos: AbstractPosition, distance: int) -> list[AbstractPosition]:
    neighbors = []
    for dx in range(distance + 1):
        dy = distance - dx
        if (dx == 0):
            neighbors.append(pos.left(dy))
            neighbors.append(pos.right(dy))
        elif (dy == 0):
            neighbors.append(pos.up(dx))
            neighbors.append(pos.down(dx))
        else:
            neighbors.append(pos.up(dx).left(dy))
            neighbors.append(pos.up(dx).right(dy))
            neighbors.append(pos.down(dx).left(dy))
            neighbors.append(pos.down(dx).right(dy))
    return neighbors

def manhattan_neighbors_range(pos: AbstractPosition, from_distance: int, to_distance: int) -> list[AbstractPosition]:
    neighbors = []
    for d in range(from_distance, to_distance + 1):
        neighbors.extend(manhattan_neighbors(pos, d))
    return neighbors

class Rule2P(AbstractClueRule):
    name = ["2P'", "旅程", "Journey"]
    doc = "线索表示距离最近的 2 个雷的曼哈顿距离之和"

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        if len([_ for _ in board("F")]) < 2:
            return board
        for pos, _ in board("N"):
            a_lay = b_lay = -1
            r = 0
            while b_lay == -1:
                r += 1
                neighbors = manhattan_neighbors(pos, r)
                count = board.batch(neighbors, mode="type").count("F")
                if (count >= 2):
                    if a_lay == -1:
                        a_lay = b_lay = r
                    else:
                        b_lay = r
                elif (count == 1):
                    if (a_lay == -1):
                        a_lay = r
                    else:
                        b_lay = r
            board.set_value(pos, Value2P(pos, bytes([a_lay + b_lay])))
        return board
  
class Value2P(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes):
        super().__init__(pos, code)
        self.value = code[0]
        self.pos = pos

    def __repr__(self) -> str:
        return f"{self.value}"
    
    @classmethod
    def type(cls) -> bytes:
        return Rule2P.name[0].encode("ascii")
    
    def code(self) -> bytes:
        return bytes([self.value])
    
    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        n = 1
        v = 0
        positions = []
        while True:
            neibors = manhattan_neighbors(self.pos, n)
            neibors = [pos for pos in neibors if board.in_bounds(pos)]
            if len(neibors) == 0:
                return []
            neibors_t = board.batch(neibors, mode="type")
            v += neibors_t.count("F") + neibors_t.count("N")
            for pos, t in zip(neibors, neibors_t):
                if t not in ["F", "N"]:
                    continue
                positions.append(pos)
            if v > 2:
                break
            n += 1
        return positions

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        logger = get_logger()
        s = switch.get(model, self)

        var_list = []
        for a in range(1, self.value // 2 + 1):
            b = self.value - a
            var = model.NewBoolVar("[2P']")
            if a == b:
                neighbors = manhattan_neighbors(self.pos, a)
                model.Add(sum(board.batch(neighbors, mode="variable", drop_none=True)) >= 2).OnlyEnforceIf([var, s])
            else:
                neighbors_a = manhattan_neighbors(self.pos, a)
                model.Add(sum(board.batch(neighbors_a, mode="variable", drop_none=True)) == 1).OnlyEnforceIf([var, s])
                neighbors_b = manhattan_neighbors(self.pos, b)
                model.Add(sum(board.batch(neighbors_b, mode="variable", drop_none=True)) >= 1).OnlyEnforceIf([var, s])
                none_var = manhattan_neighbors_range(self.pos, 1, a - 1) + manhattan_neighbors_range(self.pos, a + 1, b - 1)
                model.Add(sum(board.batch(none_var, mode="variable", drop_none=True)) == 0).OnlyEnforceIf([var, s])
            var_list.append(var)
        model.AddBoolOr(var_list).OnlyEnforceIf(s)
        logger.trace(f"pos {self.pos} value[{self}] 添加了共{len(var_list)}情况")
