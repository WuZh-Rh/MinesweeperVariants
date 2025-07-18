#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/08 11:12
# @Author  : Wu_RH
# @FileName: 2G.py
"""
[2G] 四连块 (Group)：所有四连通雷区域的面积为 4
"""
from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard
from utils.solver import get_model

from collections import defaultdict


class Rule2G(AbstractMinesRule):
    name = "2G"

    def create_constraints(self, board: AbstractBoard):
        model = get_model()

        def dfs(_board: AbstractBoard, _valides: list, step=0, checked=None, possible_list=None):
            if possible_list is None:
                possible_list = set()
            if checked is None:
                checked = []
            if step == 4:
                possible_list.add((tuple(sorted(set(_valides))), tuple(sorted(set(checked)))))
                return possible_list
            for _pos in sorted(set(_valides)):
                if _pos in checked:
                    continue
                if board.get_type(_pos) == "C":
                    continue
                checked.append(_pos)
                _valides.remove(_pos)
                pos_list = []
                for __pos in _pos.neighbors(1):
                    if __pos in checked:
                        continue
                    if __pos in _valides:
                        continue
                    if not board.in_bounds(__pos):
                        continue
                    _valides.append(__pos)
                    pos_list.append(__pos)
                dfs(_board, _valides, step + 1, checked, possible_list)
                for __pos in pos_list:
                    _valides.remove(__pos)
                checked.remove(_pos)
                _valides.append(_pos)
            return possible_list

        for pos, var in board("NF", mode="variable"):
            vaildes = [pos]

            tmp_list = []
            possible_list = dfs(board, vaildes)
            for vars_t, vars_f in possible_list:
                if any(t_pos in vars_f for t_pos in vars_t):
                    continue
                if any(f_pos in vars_t for f_pos in vars_f):
                    continue
                # print(vars_t)
                # print(vars_f)
                # print()
                vars_t = board.batch(vars_t, mode="variable")
                vars_f = board.batch(vars_f, mode="variable")
                tmp = model.NewBoolVar("tmp")
                model.Add(sum(vars_t) == 0).OnlyEnforceIf(tmp)
                model.AddBoolAnd(vars_f).OnlyEnforceIf(tmp)
                tmp_list.append(tmp)
            model.AddBoolOr(tmp_list).OnlyEnforceIf(var)

    @classmethod
    def method_choose(cls) -> int:
        return 1

    def suggest_total(self, info: dict):

        def hard_constraint(m, total):
            m.AddModuloEquality(0, total, 4)

        info["hard_fns"].append(hard_constraint)
