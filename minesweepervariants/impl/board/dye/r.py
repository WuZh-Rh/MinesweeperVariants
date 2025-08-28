#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 10:54
# @Author  : xxx
# @FileName: r.py

from ....utils.tool import get_random

from . import AbstractDye


class DyeR(AbstractDye):
    name = "r"
    __doc__ = "纯随机"

    def dye(self, board):
        random = get_random()
        for key in board.get_interactive_keys():
            pos = board.boundary(key=key)
            for _pos in board.get_row_pos(pos):
                for __pos in board.get_col_pos(_pos):
                    board.set_dyed(__pos, random.random() >= 0.5)
