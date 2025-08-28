#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/28 09:47
# @Author  : Wu_RH
# @FileName: s.py
"""
[@s]粗斜线
"""

from . import AbstractDye


class DyeC(AbstractDye):
    name = "s" # slash
    __doc__ = "粗斜线"

    def dye(self, board):
        x = 1
        for key in board.get_interactive_keys():
            pos = board.get_pos(0, 0, key)
            col = board.get_col_pos(pos)
            y = x
            for row in [board.get_row_pos(_pos) for _pos in col]:
                z = y
                for pos in row:
                    dye = z // 2 == 1
                    board.set_dyed(pos, dye)
                    z += 1
                    z = 0 if z == 4 else z
                y += 1
                y = 0 if y == 4 else y
            x += 1
            x = 0 if x == 4 else x
