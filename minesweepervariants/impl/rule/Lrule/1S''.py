from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition

from .connect import connect

class Rule1S(AbstractMinesRule):
    name = ["1S''", "S''", "传送门蛇", "Portal Snake"]
    doc = "所有雷构成一条蛇。蛇是一条宽度为 1 的四连通路径，不存在分叉、环、交叉。题板的上下左右视为连通。"

    def portalNeighbor(self, pos : AbstractPosition, board: AbstractBoard):
        boundary = board.boundary(pos.board_key)
        neighbors = pos.neighbors(1)
        result = []
        for p in neighbors:
            if board.in_bounds(p):
                result.append(p)
        if pos.x == 0:
            result.append(board.get_pos(boundary.x, pos.y))
        if pos.x == boundary.x:
            result.append(board.get_pos(0, pos.y))
        if pos.y == 0:
            result.append(board.get_pos(pos.x, boundary.y))
        if pos.y == boundary.y:
            result.append(board.get_pos(pos.x, 0))
        return result

    def create_constraints(self, board, switch):
        model = board.get_model()
        s = switch.get(model, self)

        connect(model, board, s, connect_value=1, nei_value=lambda pos: self.portalNeighbor(pos, board))

        tmp_list = []
        for pos, var in board(mode="variable"):
            tmp_bool = model.NewBoolVar(f"[1S''] {pos}")
            var_list = board.batch(self.portalNeighbor(pos, board), mode="variable", drop_none=True)
            model.Add(sum(var_list) == 1).OnlyEnforceIf([var, tmp_bool, s])
            model.Add(sum(var_list) == 2).OnlyEnforceIf([var, tmp_bool.Not(), s])
            tmp_list.append(tmp_bool)
        model.Add(sum(tmp_list) == 2).OnlyEnforceIf(s)
