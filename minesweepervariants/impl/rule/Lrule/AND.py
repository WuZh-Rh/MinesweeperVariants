#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/08 12:15
# @Author  : Wu_RH
# @FileName: OR.py
"""
[AND]与:你可以在后面输入多个左线来表示与关系(题板将按照A规则和B规则)(规则间使用":"隔开)
"""
from minesweepervariants.abs.Lrule import AbstractMinesRule
from minesweepervariants.abs.board import AbstractBoard
from minesweepervariants.config.config import PUZZLE_CONFIG

from ...impl_obj import get_rule
from ...summon.solver import Switch

CONFIG = {}
CONFIG.update(PUZZLE_CONFIG)


class RuleOR(AbstractMinesRule):
    name = ["AND", "与"]
    doc = "你可以在后面输入多个左线来表示或关系(题板将按照A规则或B规则)"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        rule_list = [""]
        deep = 0
        for s in data:
            if s == "(":
                if deep > 0:
                    rule_list[-1] += "("
                deep += 1
            elif s == ")":
                if deep > 1:
                    rule_list[-1] += ")"
                deep -= 1
            elif s == ":" and deep == 0:
                rule_list.append("")
            else:
                rule_list[-1] += s
        if len(rule_list) == 0:
            raise ValueError("你不能或空的规则")
        self.rules = []
        for rule in rule_list:
            if CONFIG["delimiter"] in rule:
                rule_name, rule_data = rule.split(CONFIG["delimiter"], 1)
            else:
                rule_name = rule
                rule_data = None
            rule = get_rule(rule_name)(board=board, data=rule_data)
            if not isinstance(rule, AbstractMinesRule):
                continue
            self.rules.append(rule)

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        model = board.get_model()
        var_list = []
        for rule in self.rules:
            z = model.NewBoolVar("AND")
            _switch = Switch()
            rule.create_constraints(board=board, switch=_switch)
            model.AddBoolAnd(_switch.get_all_vars()).OnlyEnforceIf(z)
            var_list.append(z)
        model.AddBoolAnd(var_list).OnlyEnforceIf(switch.get(model, self))

    def suggest_total(self, info: dict):
        for rule in self.rules:
            rule.suggest_total(info)
