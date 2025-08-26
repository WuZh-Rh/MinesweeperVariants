#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/09 07:14
# @Author  : Wu_RH
# @FileName: 2L'.py
"""
[2L'] 误差' (Liar')：每行每列恰有一个非误差线索。误差线索的值比真实值大 1 或小 1 [副版规则]
"""
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.impl_obj import VALUE_CIRCLE, VALUE_CROSS
from ....utils.tool import get_random, get_logger

NAME_2L = "2L"


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


class Rule2L(AbstractClueRule):
    name = ["2L'", "误差'", "Liar'"]
    doc = "每行每列恰有一个非误差线索。误差线索的值比真实值大 1 或小 1"

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
        board.generate_board(NAME_2L, (bound.x + 1, bound.y + 1))

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        logger = get_logger()
        boundary = board.boundary()
        keys = board.get_interactive_keys()

        matrix = []
        for x in range(boundary.x + 1):
            row = []
            for y in range(boundary.y + 1):
                row.append(all(
                    board.get_type(board.get_pos(x, y, key)) != "F"
                    for key in keys
                ))
            matrix.append(row)

        pos_map = select(matrix)

        if not pos_map:
            raise ValueError("[2L]: has a line is all mines")

        for pos, _ in board("N"):
            value = board.batch(pos.neighbors(2), mode="type").count("F")
            if not (pos.x, pos.y) in pos_map:
                value = random.choice([value + 1, value - 1])
                if value == -1:
                    value = 1
                if value == 9:
                    value = 7
                obj = Value2L(pos, bytes([random.choice([value])]))
            else:
                obj = Value2L(pos, bytes([value]))
            board.set_value(pos, obj)
            logger.debug(f"[2L]put {obj} to {pos}")

        for pos, _ in board(key=NAME_2L):
            if (pos.x, pos.y) in pos_map:
                board.set_value(pos, VALUE_CIRCLE)
                logger.debug(f"[2L]put O to {pos}")
            else:
                board.set_value(pos, VALUE_CROSS)
                logger.debug(f"[2L]put X to {pos}")

        return board

    def init_clear(self, board: 'AbstractBoard'):
        for pos, _ in board(key=NAME_2L):
            board.set_value(pos, None)

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        bound = board.boundary(key=NAME_2L)

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

        for pos, _ in board(key=NAME_2L):
            _pos = pos.clone()
            var = board.get_variable(pos)
            for key in board.get_interactive_keys():
                _pos.board_key = key
                key_var = board.get_variable(_pos)
                model.Add(key_var == 0).OnlyEnforceIf([var, s])


class Value2L(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.nei = pos.neighbors(2)
        self.pos = pos.clone()
        self.pos.board_key = NAME_2L

    def __repr__(self) -> str:
        return str(self.value)

    @classmethod
    def method_choose(cls) -> int:
        return 1

    @classmethod
    def type(cls) -> bytes:
        return Rule2L.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        nei_vars = board.batch(self.nei, mode="variable", drop_none=True)
        var = board.get_variable(self.pos)

        model.Add(sum(nei_vars) == self.value).OnlyEnforceIf([var, s])

        tmp_a = model.NewBoolVar("tmp_a")
        tmp_b = model.NewBoolVar("tmp_b")

        model.Add(sum(nei_vars) == self.value + 1).OnlyEnforceIf([tmp_a, var.Not(), s])
        model.Add(sum(nei_vars) == self.value - 1).OnlyEnforceIf([tmp_b, var.Not(), s])

        model.AddBoolOr([tmp_a, tmp_b]).OnlyEnforceIf(s)
