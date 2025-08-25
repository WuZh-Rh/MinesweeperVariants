#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/13 23:00
# @Author  : Wu_RH
# @FileName: 3P.py
"""
[3P]游行(Parade):可以通过骑士的移动方式，从某一个雷格开始，在只经过雷格的情况下，不重复且不遗漏地通过所有雷格
[3P]游行(Parade):可以通过雷与该雷马步格的雷链接的图形成哈密顿路径
[3P]游行(Parade):可以通过从某格雷出发每次走马步格随后一笔画完所有雷
"""
from minesweepervariants.abs.Lrule import AbstractMinesRule
from minesweepervariants.abs.board import AbstractBoard, AbstractPosition
from minesweepervariants.impl.summon.solver import Switch


class Rule3P(AbstractMinesRule):
    name = ["3P", "游行", "Parade"]
    doc = "可以通过骑士的移动方式，从某一个雷格开始，在只经过雷格的情况下，不重复且不遗漏地通过所有雷格"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        self.nei_values = []
        if data is None:
            self.nei_values = [tuple([5])]
            return
        nei_values = data.split(";")
        for nei_value in nei_values:
            if ":" in nei_value:
                self.nei_values.append(tuple([
                    int(nei_value.split(":")[0]),
                    int(nei_value.split(":")[1])
                ]))
            else:
                self.nei_values.append(tuple([int(nei_value)]))

    def nei_pos(self, board: AbstractBoard, pos: AbstractPosition):
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
        return [pos for pos in positions if board.is_valid(pos)]

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        model = board.get_model()
        s = switch.get(model, self)

        root_map = {pos: model.NewBoolVar(f"root[{pos}]") for pos, _ in board()}
        id_map = {}

        for key in board.get_interactive_keys():
            positions = [pos for pos, _ in board(key=key)]
            for pos in positions:
                id_map[pos] = model.NewIntVar(0, len(positions), f"id[{pos}]")
            model.Add(sum(map(root_map.get, positions)) == 1).OnlyEnforceIf(s)

        for pos, var in board(mode="var"):
            model.Add(root_map[pos] == 0).OnlyEnforceIf([var.Not(), s])
            model.Add(id_map[pos] == 1).OnlyEnforceIf([root_map[pos], s])
            model.Add(id_map[pos] == 0).OnlyEnforceIf([var.Not(), s])
            model.Add(id_map[pos] > 0).OnlyEnforceIf([var, s])

        for pos, var in board(mode="var"):
            nei_pos = self.nei_pos(board, pos)
            tmp_list = []
            for _pos in nei_pos:
                tmp = model.NewBoolVar(f"tmp[{pos}->{_pos}]")
                _var = board.get_variable(_pos)
                model.Add(id_map[pos] == id_map[_pos] + 1).OnlyEnforceIf([tmp, s])
                model.Add(_var == 1).OnlyEnforceIf([tmp, s])
                tmp_list.append(tmp)
            for _pos1 in nei_pos:
                for _pos2 in nei_pos:
                    if _pos1 == _pos2:
                        continue
                    model.Add(id_map[_pos1] != id_map[_pos2]).OnlyEnforceIf([
                        board.get_variable(_pos1),
                        board.get_variable(_pos2),
                        var, s, root_map[_pos1].Not(),
                        root_map[_pos2].Not()
                    ])
            model.AddBoolOr(tmp_list).OnlyEnforceIf([var, root_map[pos].Not(), s])

        # for pos1, var1 in board(mode="var"):
        #     for pos2, var2 in board(mode="var"):
        #         if pos1 == pos2:
        #             continue
        #         model.Add(id_map[pos1] != id_map[pos2]).OnlyEnforceIf([
        #             var1, var2, root_map[pos1].Not(),
        #             root_map[pos2].Not(), s
        #         ])
