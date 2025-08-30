#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/10 03:17
# @Author  : Wu_RH
# @FileName: 2G'.py
"""
[2G'] 三连块 (Group')：所有四连通雷区域的面积为 3
"""
# (在提示的表现似乎有问题)
from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard


class Rule2Gp(AbstractMinesRule):
    name = ["2G'", "三连块", "Group'"]
    doc = "所有四连通雷区域的面积为3"

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        for pos, var in board(mode="variable"):
            nei = board.batch(pos.neighbors(1), mode="variable", drop_none=True)
            model.Add(sum(nei) < 3).OnlyEnforceIf([var, s])
            model.Add(sum(nei) > 0).OnlyEnforceIf([var, s])
            tmp = model.NewBoolVar("tmp")
            model.Add(sum(nei) == 2).OnlyEnforceIf([tmp, s])
            model.Add(sum(nei) != 2).OnlyEnforceIf([tmp.Not(), s])
            for _pos in pos.neighbors(1):
                if not board.is_valid(_pos):
                    continue
                _var = board.get_variable(_pos)
                nei = board.batch(_pos.neighbors(1), mode="variable", drop_none=True)
                model.Add(sum(nei) == 1).OnlyEnforceIf([_var, var, tmp, s])
                model.Add(sum(nei) == 2).OnlyEnforceIf([_var, var, tmp.Not(), s])

    def suggest_total(self, info: dict):
        def hard_constraint(m, total):
            m.AddModuloEquality(0, total, 3)

        info["hard_fns"].append(hard_constraint)
