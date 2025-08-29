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

class RuleNSharp(AbstractClueSharp):
    name = ["N#", "标签", "Tag"]
    doc = "线索只有一个取值"

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        self.value = int(data)
        if (self.value == 0):
            rules_name = ["1L", "1N", "1E'", "1M1N", "1N1X", "2M", "2X'"]
        else:
            rules_name = ["V", "1M", "1L", "1W", "1N", "1X", "1P", "1E", "1X'", "1K", "1W'", "1E'", "1M1N", "1L1M", "1M1X", "1N1X", "2X", "2D", "2P", "2M", "2A", "2X'"]
        super().__init__(rules_name, board, data)

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        boards : list[AbstractBoard] = []
        random = get_random()
        for rule in self.shape_rule.rules:
            boards.append(rule.fill(board.clone()))
        for key in board.get_board_keys():
            for pos, _ in board("N", key=key):
                values = [_board.get_value(pos) for _board in boards if self.only_has_one_number(_board.get_value(pos))]
                if not values:
                    board.set_value(pos, VALUE_QUESS)
                else:
                    board.set_value(pos, random.choice(values))
        return board

    def only_has_one_number(self, clue) -> bool:
        clue_type = type(clue).__module__.split(".")[-1]
        repr = clue.__repr__()
        if (clue_type == "1W"):
            return all(int(x) == self.value for x in repr.split("."))
        elif (clue_type == "2X"):
            return all(int(x) == self.value for x in repr.split(" "))
        elif (clue_type == "1E'"):
            return abs(int(repr)) == self.value
        else:
            return repr == str(self.value)
