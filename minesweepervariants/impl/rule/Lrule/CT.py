"""
[CT] 仙人掌 (Cactus)：每个雷周围四格中恰有1或3个雷。
"""

from minesweepervariants.abs.Lrule import AbstractMinesRule
from minesweepervariants.abs.board import AbstractBoard
from minesweepervariants.impl.summon.solver import Switch

class RuleCT(AbstractMinesRule):
    name = ["CT", "仙人掌", "Cactus"]
    doc = "每个雷周围四格中恰有1或3个雷"

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        model = board.get_model()
        s = switch.get(model, self)
        for pos, var in board(mode="var"):
            var_list = board.batch(pos.neighbors(1), mode="var", drop_none=True)
            sum_var = model.NewIntVar(0, len(var_list), "[CT]")
            model.Add(sum(var_list) == sum_var)
            model.AddAllowedAssignments([sum_var], [[1], [3]]).OnlyEnforceIf([var, s])