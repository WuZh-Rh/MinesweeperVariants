"""
[2M''] 多雷：每行每列恰有一个雷被视为两个(总雷数不受限制)
"""

from ....abs.board import AbstractBoard, AbstractPosition
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....utils.impl_obj import VALUE_CIRCLE, VALUE_CROSS
from ....utils.tool import get_random, get_logger

NAME_2M = "2M''"


def select(matrix: list[list[bool]]) -> list[tuple[int, int]]:
    rnd = get_random()
    n = len(matrix)

    graph = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if matrix[i][j]:  # False 是可选项
                graph[i].append(j)

    for g in graph:
        rnd.shuffle(g)

    match_to = [-1] * n

    def dfs(_u: int, _visited: list[bool]) -> bool:
        for v in graph[_u]:
            if not _visited[v]:
                _visited[v] = True
                if match_to[v] == -1 or dfs(match_to[v], _visited):
                    match_to[v] = _u
                    return True
        return False

    for u in range(n):
        visited = [False] * n
        if not dfs(u, visited):
            return []

    return [(match_to[j], j) for j in range(n)]


class Rule2M(AbstractClueRule):
    name = ["2M''", "多雷", "Multiple"]
    doc = "每行每列恰有一个雷被视为两个(总雷数不受限制)"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        bound = board.boundary()
        if bound.x != bound.y:
            raise ValueError("请输入一个正方形题板")
        for key in board.get_interactive_keys():
            _bound = board.boundary(key)
            if (_bound.x != bound.x and
                    _bound.y != bound.y):
                raise ValueError("请保证其他题板尺寸均一致")
        board.generate_board(NAME_2M, (bound.x + 1, bound.y + 1))

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        boundary = board.boundary()
        keys = board.get_interactive_keys()

        matrix = []
        for x in range(boundary.x + 1):
            row = []
            for y in range(boundary.y + 1):
                row.append(all(
                    board.get_type(board.get_pos(x, y, key)) == "F"
                    for key in keys
                ))
            matrix.append(row)

        pos_map = select(matrix)

        if not pos_map:
            raise ValueError("[2M]: has a line is all non-mines")

        for pos, _ in board("N"):
            count = 0
            neighbors = pos.neighbors(2)
            for neighbor in neighbors:
                if board.get_type(neighbor) == "F":
                    if (neighbor.x, neighbor.y) in pos_map:
                        count += 2
                    else:
                        count += 1
            board.set_value(pos, Value2M(pos, bytes([count])))
            logger.debug(f"[2M]: put {count} to {pos}")

        for pos, _ in board(key=NAME_2M):
            if (pos.x, pos.y) in pos_map:
                board.set_value(pos, VALUE_CIRCLE)
                logger.debug(f"[2M]put O to {pos}")
            else:
                board.set_value(pos, VALUE_CROSS)
                logger.debug(f"[2M]put X to {pos}")

        return board

    def init_clear(self, board: 'AbstractBoard'):
        for pos, _ in board(key=NAME_2M):
            board.set_value(pos, None)

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        bound = board.boundary(key=NAME_2M)

        row = board.get_row_pos(bound)
        for pos in row:
            line = board.get_col_pos(pos)
            line_var = board.batch(line, mode="variable", drop_none=True)
            model.Add(sum(line_var) == 1).OnlyEnforceIf(s)

        col = board.get_col_pos(bound)
        for pos in col:
            line = board.get_row_pos(pos)
            line_var = board.batch(line, mode="variable", drop_none=True)
            model.Add(sum(line_var) == 1).OnlyEnforceIf(s)

        for pos, _ in board(key=NAME_2M):
            _pos = pos.clone()
            var = board.get_variable(pos)
            for key in board.get_interactive_keys():
                _pos.board_key = key
                key_var = board.get_variable(_pos)
                model.Add(key_var == 1).OnlyEnforceIf([var, s])


class Value2M(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.nei = pos.neighbors(2)
        self.pos = pos

    def __repr__(self) -> str:
        return str(self.value)
    
    @classmethod
    def type(cls) -> bytes:
        return Rule2M.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])
    
    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.nei
    
    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        vals = []
        for pos in self.nei:
            if not board.in_bounds(pos):
                continue
            z = model.NewIntVar(0, 2, f"[2M]{pos}")
            a = board.get_variable(pos)
            pos2M = pos.clone()
            pos2M.board_key = NAME_2M
            b = board.get_variable(pos2M)
            model.Add(z == 0).OnlyEnforceIf(a.Not())
            model.Add(z == 1).OnlyEnforceIf([a, b.Not()])
            model.Add(z == 2).OnlyEnforceIf([a, b])
            vals.append(z)
        if vals:
            model.Add(sum(vals) == self.value).OnlyEnforceIf(s)
