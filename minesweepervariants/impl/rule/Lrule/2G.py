#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/08 11:12
# @Author  : Wu_RH
# @FileName: 2G.py
"""
[2G] 四连块 (Group)：所有四连通雷区域的面积为 4
"""
from ....abs.Lrule import AbstractMinesRule
from ....abs.board import AbstractBoard, AbstractPosition


class Rule2G(AbstractMinesRule):
    name = ["2G", "四连块", "Group"]
    doc = "所有四连通雷区域的面积为 4"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        self.nei_values = []
        if data is None:
            self.nei_values = [tuple([1])]
            self.value = 4
            return
        nei_values = "1"
        if ";;" in data:
            nei_values = data.split(";;")[0]
            self.value = int(data.split(";;")[1])
            if self.value > 6:
                raise ValueError("连块数量禁止超过6")
        if nei_values == "":
            nei_values = "1"
        nei_values = nei_values.split(";")
        for nei_value in nei_values:
            if ":" in nei_value:
                self.nei_values.append(tuple([
                    int(nei_value.split(":")[0]),
                    int(nei_value.split(":")[1])
                ]))
            else:
                self.nei_values.append(tuple([int(nei_value)]))

    def nei_pos(self, pos: AbstractPosition):
        positions = []
        for nei_value in self.nei_values:
            if len(nei_value) == 1:
                positions.extend(
                    pos.neighbors(nei_value[0], nei_value[0])
                )
            elif len(nei_value) == 2:
                positions.extend(
                    pos.neighbors(nei_value[0], nei_value[1])
                )
        return positions

    def create_constraints(self, board: AbstractBoard, switch):
        model = board.get_model()
        s = switch.get(model, self)

        def dfs(_board: AbstractBoard, _valides: list, step=0, checked=None, _possible_list=None):
            if _possible_list is None:
                _possible_list = set()
            if checked is None:
                checked = []
            if step == self.value:
                _possible_list.add((tuple(sorted(set(_valides))), tuple(sorted(set(checked)))))
                return _possible_list
            for _pos in sorted(set(_valides)):
                if _pos in checked:
                    continue
                if board.get_type(_pos) == "C":
                    continue
                checked.append(_pos)
                _valides.remove(_pos)
                pos_list = []
                for __pos in self.nei_pos(_pos):
                    if __pos in checked:
                        continue
                    if __pos in _valides:
                        continue
                    if not board.in_bounds(__pos):
                        continue
                    _valides.append(__pos)
                    pos_list.append(__pos)
                dfs(_board, _valides, step + 1, checked, _possible_list)
                for __pos in pos_list:
                    _valides.remove(__pos)
                checked.remove(_pos)
                _valides.append(_pos)
            return _possible_list

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
                model.Add(sum(vars_t) == 0).OnlyEnforceIf([tmp, s])
                model.AddBoolAnd(vars_f).OnlyEnforceIf([tmp, s])
                tmp_list.append(tmp)
            model.AddBoolOr(tmp_list).OnlyEnforceIf([var, s])

    def suggest_total(self, info: dict):

        def hard_constraint(m, total):
            m.AddModuloEquality(0, total, self.value)

        info["hard_fns"].append(hard_constraint)
