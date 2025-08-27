"""
[#]标签: 线索会有不同的规则, 每个线索的规则会单独标出
"""
from typing import List, Tuple, Optional

from ....abs.Rrule import AbstractClueRule
from ....abs.board import AbstractBoard
from ....abs.rule import AbstractRule
from ....utils.tool import get_random, get_logger
from ...impl_obj import get_rule
from ....utils.impl_obj import VALUE_QUESS

from . import AbstractClueSharp

class Rule0Sharp(AbstractClueSharp):
    name = ["0#", "标签", "Tag"]
    doc = "包含以下规则 [1L], [1N], [1E'], [1M1N], [1N1X], [2M], [2X']。线索值只有零。"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        rules_name = ["1L", "1N", "1E'", "1M1N", "1N1X", "2M", "2X'"]
        super().__init__(rules_name, board, data)
        self.rules = data

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        boards : list[AbstractBoard] = []
        random = get_random()
        for rule in self.shape_rule.rules:
            boards.append(rule.fill(board.clone()))
        for key in board.get_board_keys():
            for pos, _ in board("N", key=key):
                values = [_board.get_value(pos) for _board in boards if _board.get_value(pos).__repr__() == '0']
                if not values:
                    board.set_value(pos, VALUE_QUESS)
                else:
                    board.set_value(pos, random.choice(values))
        return board