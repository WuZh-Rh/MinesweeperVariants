#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/28 10:12
# @Author  : Wu_RH
# @FileName: l.py

from . import AbstractDye


class DyeC(AbstractDye):
    name = "l"
    __doc__ = "全盘染色"

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                _dye = dye ^ (pos.y % 2 > 0)
                board.set_dyed(pos, _dye)
