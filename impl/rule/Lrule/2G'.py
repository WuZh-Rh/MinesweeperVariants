#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/10 03:17
# @Author  : Wu_RH
# @FileName: 2G'.py
"""
[2G'] 三连块 (Group')：所有四连通雷区域的面积为 3 (在提示的表现似乎有问题)
"""
from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard
from utils.solver import get_model


class Rule2Gp(AbstractMinesRule):
    name = "2G'"
    subrules = [[True, "[2G']三联块"]]

    @classmethod
    def method_choose(cls) -> int:
        return 1

    def create_constraints(self, board: 'AbstractBoard'):
        if not self.subrules[0][0]:
            return
        model = get_model()
        for pos, var in board(mode="variable"):
            nei = board.batch(pos.neighbors(1), mode="variable", drop_none=True)
            model.Add(sum(nei) < 3).OnlyEnforceIf(var)
            model.Add(sum(nei) > 0).OnlyEnforceIf(var)
            tmp = model.NewBoolVar("tmp")
            model.Add(sum(nei) == 2).OnlyEnforceIf(tmp)
            model.Add(sum(nei) != 2).OnlyEnforceIf(tmp.Not())
            for _pos in pos.neighbors(1):
                if not board.is_valid(_pos):
                    continue
                _var = board.get_variable(_pos)
                nei = board.batch(_pos.neighbors(1), mode="variable", drop_none=True)
                model.Add(sum(nei) == 1).OnlyEnforceIf([_var, var, tmp])
                model.Add(sum(nei) == 2).OnlyEnforceIf([_var, var, tmp.Not()])

    def suggest_total(self, info: dict):
        def hard_constraint(m, total):
            m.AddModuloEquality(0, total, 3)

        info["hard_fns"].append(hard_constraint)
