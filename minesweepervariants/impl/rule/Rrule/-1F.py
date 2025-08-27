#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/07 23:45
# @Author  : Wu_RH
# @FileName: -1F.py
"""
[*1F]翻转(Flip): 线索表示其以题板左上角到右下角直线为对称轴的镜像位置周围八格的雷数，不包括自身
"""
from typing import List

from minesweepervariants.abs.Rrule import AbstractClueValue, AbstractClueRule
from minesweepervariants.abs.board import AbstractPosition, AbstractBoard
from minesweepervariants.impl.summon.solver import Switch


class Rulex1F(AbstractClueRule):
    name = ["*1F", "翻转", "Filp"]
    doc = "线索表示其以题板左上角到右下角直线为对称轴的镜像位置周围八格的雷数，不包括自身"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        for pos, _ in board("N"):
            _pos = pos.clone()
            _pos.x, _pos.y = _pos.y, _pos.x
            value = board.batch(_pos.neighbors(2), mode="type").count("F")
            board.set_value(pos, Valuex1F(pos, code=bytes([value])))
        return board


class Valuex1F(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.pos = pos
        self.value = code[0]

    def __repr__(self):
        return str(self.value)

    def code(self) -> bytes:
        return bytes([self.value])

    def high_light(self, board: 'AbstractBoard') -> List['AbstractPosition'] | None:
        pos = self.pos.clone()
        pos.x, pos.y = pos.y, pos.x
        return pos.neighbors(2)

    @classmethod
    def type(cls) -> bytes:
        return Rulex1F.name[0].encode("ascii")

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        model = board.get_model()
        s = switch.get(model, self)
        pos = self.pos.clone()
        pos.x, pos.y = pos.y, pos.x
        var_list = board.batch(pos.neighbors(2), mode="variable", drop_none=True)
        model.Add(sum(var_list) == self.value).OnlyEnforceIf(s)

