from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition

from .connect import connect

class Rule1C(AbstractMinesRule):
    name = ["1C'", "C'", "八连通'", "Connected'"]
    doc = "(1) 染色格的雷和 (2) 非染色格的雷各自八连通。染色区域和非染色区域至少有一个雷。"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s1 = switch.get(model, self)
        s2 = switch.get(model, self)
        dyed_vars = []
        undyed_vars = []
        for pos, var in board(mode="variable"):
            dyed = board.get_dyed(pos)
            if dyed:
                dyed_vars.append((pos, var))
                undyed_vars.append((pos, model.NewConstant(0)))
            else:
                dyed_vars.append((pos, model.NewConstant(0)))
                undyed_vars.append((pos, var))
        model.AddBoolOr([d[1] for d in dyed_vars]).OnlyEnforceIf(s1)
        model.AddBoolOr([u[1] for u in undyed_vars]).OnlyEnforceIf(s2)
        connect(model, board, s1, positions_vars=dyed_vars)
        connect(model, board, s2, positions_vars=undyed_vars)
