#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 11:40
# @Author  : xxx
# @FileName: sharp.py
"""
[#]标签: 线索会有不同的规则, 每个线索的规则会单独标出
"""
from typing import List, Tuple, Optional

from ....abs.Mrule import AbstractMinesClueRule
from ....abs.board import AbstractBoard
from ....abs.rule import AbstractRule
from ....utils.tool import get_random


class RuleSharp(AbstractMinesClueRule):
    name = ["#", "标签", "Tag"]
    doc = "线索会有不同的规则, 每个线索的规则会单独标出"

    def __init__(self, board: AbstractBoard, data: list[AbstractMinesClueRule]):
        super().__init__(board, None)
        self.rules = data
        for key in board.get_interactive_keys():
            board.set_config(key, "by_mini", True)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        boards = []
        for rule in self.rules:
            boards.append(rule.fill(board.clone()))
        for key in board.get_board_keys():
            for pos, _ in board("F", key=key):
                values = [_board.get_value(pos)
                          for _board in boards
                          if _board.get_type(pos) != "N"]
                if not values:
                    continue
                board.set_value(pos, get_random().choice(values))
        return board

    def combine(self, rules: List[Tuple['AbstractRule', Optional[str]]]):
        for rule in self.rules:
            rule.combine(rules)

    def suggest_total(self, info: dict):
        for rule in self.rules:
            rule.suggest_total(info)

    def init_board(self, board: 'AbstractBoard'):
        for rule in self.rules:
            rule.init_board(board)

    def init_clear(self, board: 'AbstractBoard'):
        for rule in self.rules:
            rule.init_clear(board)

    def create_constraints(self, board: 'AbstractBoard', switch):
        for rule in self.rules:
            rule.create_constraints(board, switch)
