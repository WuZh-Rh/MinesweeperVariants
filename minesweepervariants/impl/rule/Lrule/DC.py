"""
[DC] 必对角 (Diagonally Connected)：每个雷对角相邻的四格中有至少一个雷
"""

from minesweepervariants.abs.Lrule import AbstractMinesRule
from minesweepervariants.abs.board import AbstractBoard
from minesweepervariants.impl.summon.solver import Switch

class RuleDC(AbstractMinesRule):
    name = ["DC", "必对角", "Diagonally Connected"]
    doc = "每个雷对角相邻的四格中有至少一个雷"

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        model = board.get_model()
        s = switch.get(model, self)
        for pos, var in board(mode="var"):
            var_list = board.batch(pos.neighbors(2, 2), mode="var", drop_none=True)
            model.Add(sum(var_list) >= 1).OnlyEnforceIf([var, s])
