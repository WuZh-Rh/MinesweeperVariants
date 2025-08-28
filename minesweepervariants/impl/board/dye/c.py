#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 09:52
# @Author  : xxx
# @FileName: c.py

from . import AbstractDye


class DyeC(AbstractDye):
    name = "c" # checkerboard
    __doc__ = "棋盘格染色"

    def __init__(self, args):
        if args:
            self.offset = 1
        else:
            self.offset = 0

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                _dye = dye ^ ((pos.x + pos.y + self.offset) % 2 > 0)
                board.set_dyed(pos, _dye)
