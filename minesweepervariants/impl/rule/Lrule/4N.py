from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition

class Rule4N(AbstractMinesRule):
    name = ["4N", "4N", "相邻"]
    doc = "非雷周围四格必须有雷"

    def create_constraints(self, board, switch):
        model = board.get_model()
        s = switch.get(model, self)

        for pos, var in board(mode="variable"):
            model.AddBoolOr(board.batch(pos.neighbors(1), mode="variable", drop_none=True)).OnlyEnforceIf([var.Not(), s])
