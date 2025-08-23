"""
[1X2X] 线索代表半径为 2 的十字范围内中，染色和非染色格里的雷数(顺序不确定)
"""
from typing import List, Dict

from minesweepervariants.utils.web_template import MultiNumber
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.image_create import get_text, get_row

from ....utils.tool import get_logger, get_random

def cross_neighbors(pos : AbstractPosition) -> list[AbstractPosition]:
    return [
        pos.up(2),
        pos.down(2),
        pos.left(2),
        pos.right(2),
        pos.up(1),
        pos.down(1),
        pos.left(1),
        pos.right(1)
    ]

class Rule1X2X(AbstractClueRule):
    name = ["1X2X", "十字"]
    doc = "线索代表半径为 2 的十字范围内中，染色和非染色格里的雷数(顺序不确定)"

    def clue_class(self):
        return Value1X2X

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        r = get_random()
        for pos, _ in board("N"):
            value1 = len([_pos for _pos in cross_neighbors(pos) if board.get_type(_pos) == "F" and board.get_dyed(_pos)])
            value2 = len(
                [_pos for _pos in cross_neighbors(pos) if board.get_type(_pos) == "F" and not board.get_dyed(_pos)])
            if r.randint(0, 1): value1, value2 = value2, value1
            board.set_value(pos, Value1X2X(pos, count=value1 * 10 + value2))
            logger.debug(f"Set {pos} to 1X2X[{value1 * 10 + value2}]")
        return board


class Value1X2X(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', count: int = 0, code: bytes = None):
        super().__init__(pos, code)
        if code is not None:
            self.count = code[0]
        else:
            self.count = count
        self.neighbor = cross_neighbors(pos)

    def __repr__(self) -> str:
        return f"{self.count // 10} {self.count % 10}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbor

    def web_component(self, board) -> Dict:
        value = [self.count // 10, self.count % 10]
        value.sort()
        return MultiNumber(value)

    def compose(self, board) -> Dict:
        value = [self.count // 10, self.count % 10]
        value.sort()
        text_a = get_text(str(value[0]))
        text_b = get_text(str(value[1]))
        return get_row(
            text_a,
            text_b
        )

    @classmethod
    def type(cls) -> bytes:
        return Rule1X2X.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.count])

    def create_constraints(self, board: 'AbstractBoard', switch):
        """创建CP-SAT约束: 周围染色格雷数等于两个染色格的数量"""
        model = board.get_model()
        s = switch.get(model, self)

        # 收集周围格子的布尔变量
        neighbor_vars1 = []
        neighbor_vars2 = []
        for neighbor in self.neighbor:  # 8方向相邻格子
            if board.in_bounds(neighbor):
                if board.get_dyed(neighbor):
                    var = board.get_variable(neighbor)
                    neighbor_vars1.append(var)
                else:
                    var = board.get_variable(neighbor)
                    neighbor_vars2.append(var)

        if neighbor_vars1 or neighbor_vars2:
            # 定义变量
            t = model.NewBoolVar('t')
            # 设置A B C D的值
            model.Add(sum(neighbor_vars1) == self.count // 10).OnlyEnforceIf([t, s])
            model.Add(sum(neighbor_vars2) == self.count % 10).OnlyEnforceIf([t, s])
            model.Add(sum(neighbor_vars1) == self.count % 10).OnlyEnforceIf([t.Not(), s])
            model.Add(sum(neighbor_vars2) == self.count // 10).OnlyEnforceIf([t.Not(), s])
