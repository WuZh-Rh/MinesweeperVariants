#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/08/25 17:53
# @Author  : Wu_RH
# @FileName: mate.py
"""
[MATE]原神:题板具有多块主板,多块主板的雷位置完全相同,但是题板具有不同的线索,规则将按照顺序标出
参数: 可以输入多个右线 随后初始化多个题板(如果存在其他多主板规则需要提前初始化)
例: MATE:2M:V
"""
from typing import List, Tuple, Optional

from minesweepervariants.abs.Rrule import AbstractClueRule
from minesweepervariants.abs.board import AbstractBoard, MASTER_BOARD
from minesweepervariants.abs.rule import AbstractRule
from minesweepervariants.impl.impl_obj import get_rule

from minesweepervariants.impl.rule.Rrule.V import RuleV
from minesweepervariants.impl.summon.solver import Switch
from minesweepervariants.utils.impl_obj import MINES_TAG, VALUE_QUESS


class RuleMate(AbstractClueRule):
    name = ["MATE", "Mate", "mate", "元"]
    doc = "题板具有多块主板,多块主板的雷位置完全相同,但是题板具有不同的规则,规则将按照顺序标出"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        super().__init__(board, data)
        if data is None:
            raise ValueError("请输入右线id")
        rule_names = data.split(":")
        self.rules = []
        for name in rule_names:
            rule = get_rule(name)(board=board, data=None)
            self.rules.append(rule)
        for _ in range(len(board.get_interactive_keys()) - len(self.name)):
            self.rules.append(RuleV())
        size = board.get_config(MASTER_BOARD, "size")
        for key in board.get_interactive_keys():
            board.set_config(key, "by_mini", True)
        for i in range(
            len(self.rules) -
            len(board.get_interactive_keys())
        ):
            board.generate_board("MATE" + str(i), size=size)
            board.set_config("MATE" + str(i), "interactive", True)
            board.set_config("MATE" + str(i), "row_col", True)
            board.set_config("MATE" + str(i), "by_mini", True)
            board.set_config("MATE" + str(i), "MINES", MINES_TAG)
            board.set_config("MATE" + str(i), "VALUE", VALUE_QUESS)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        if len(board.get_interactive_keys()) < len(self.rules):
            raise ValueError("初始化失败")
        board_dict = {}
        for key, rule in zip(board.get_interactive_keys(), self.rules):
            _board = board.clone()
            rule: AbstractClueRule
            rule.fill(board=_board)
            board_dict[key] = _board
        for key in board.get_interactive_keys():
            for pos, _ in board(key=key):
                board[pos] = board_dict[key][pos]
        return board

    def create_constraints(self, board: 'AbstractBoard', switch: 'Switch'):
        size = board.get_config(MASTER_BOARD, "size")
        for key in board.get_interactive_keys():
            if board.get_config(key, "size") != size:
                raise ValueError("题板尺寸不匹配")
        model = board.get_model()
        for rule in self.rules:
            rule.create_constraints(board=board, switch=switch)
        s = switch.get(model, self)
        for pos, _ in board(mode="none"):
            var_list = []
            for key in board.get_interactive_keys():
                _pos = pos.clone()
                _pos.board_key = key
                var_list.append(board.get_variable(_pos))
            for i in range(1, len(var_list)):
                model.Add(var_list[0] == var_list[i]).OnlyEnforceIf(s)

    def suggest_total(self, info: dict):
        for rule in self.rules:
            rule.suggest_total(info)

        def a(model, total):
            model.AddModuloEquality(0, total, len(self.rules))
        info["hard_fns"].append(a)

    def init_board(self, board: 'AbstractBoard'):
        for rule in self.rules:
            rule.init_board(board)

    def init_clear(self, board: 'AbstractBoard'):
        for rule in self.rules:
            rule.init_clear(board)

    def combine(self, rules: List[Tuple['AbstractRule', Optional[str]]]):
        for rule in self.rules:
            rule.combine(rules)
