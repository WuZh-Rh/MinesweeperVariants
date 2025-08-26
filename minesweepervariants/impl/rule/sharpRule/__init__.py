#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/23 22:35
# @Author  : Wu_RH
# @FileName: root_shape.py
from abc import ABC
from typing import Tuple, List, Optional

from minesweepervariants.abs.Rrule import AbstractClueRule
from minesweepervariants.abs.Mrule import AbstractMinesClueRule
from minesweepervariants.abs.board import AbstractBoard
from minesweepervariants.abs.rule import AbstractRule
from minesweepervariants.impl.impl_obj import get_rule
from minesweepervariants.impl.rule.Rrule.sharp import RuleSharp as ClueSharp
from minesweepervariants.impl.rule.Mrule.sharp import RuleSharp as MinesSharp
from minesweepervariants.impl.summon.solver import Switch
from minesweepervariants.utils.tool import get_logger


class AbstractMinesSharp(AbstractMinesClueRule, ABC):
    def __init__(self, rules: list[str], board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        rule_list = []
        for name in rules:
            try:
                rule_list.append(get_rule(name)(board=board, data=None))
            except Exception as e:
                get_logger().warn(f"加载规则:[{name}]失败")
                get_logger().warn(f"ERROR: {e}")
        self.shape_rule = MinesSharp(board=board, data=rule_list)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        return self.shape_rule.fill(board=board)

    def init_board(self, board: 'AbstractBoard'):
        return self.shape_rule.init_board(board=board)

    def init_clear(self, board: 'AbstractBoard'):
        return self.shape_rule.init_clear(board=board)

    def combine(self, rules: List[Tuple['AbstractRule', Optional[str]]]):
        return self.shape_rule.combine(rules=rules)

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        return self.shape_rule.create_constraints(board=board, switch=switch)

    def suggest_total(self, info: dict):
        return self.shape_rule.suggest_total(info=info)


class AbstractClueSharp(AbstractClueRule, ABC):
    def __init__(self, rules: list[str], board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        rule_list = []
        for name in rules:
            try:
                rule_list.append(get_rule(name)(board=board, data=None))
            except Exception as e:
                get_logger().warn(f"加载规则:[{name}]失败")
                get_logger().warn(f"ERROR: {e}")
        self.shape_rule = ClueSharp(board=board, data=rule_list)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        return self.shape_rule.fill(board=board)

    def init_board(self, board: 'AbstractBoard'):
        return self.shape_rule.init_board(board=board)

    def init_clear(self, board: 'AbstractBoard'):
        return self.shape_rule.init_clear(board=board)

    def combine(self, rules: List[Tuple['AbstractRule', Optional[str]]]):
        return self.shape_rule.combine(rules=rules)

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        return self.shape_rule.create_constraints(board=board, switch=switch)

    def suggest_total(self, info: dict):
        return self.shape_rule.suggest_total(info=info)

