#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 09:52
# @Author  : xxx
# @FileName: c.py

from . import AbstractDye


class DyeC(AbstractDye):
    name = "q"
    __doc__ = "2x2棋盘格染色"

    def __init__(self, args):
        if args is not None and args.isdigit():
            self.offset = int(args)
        else:
            self.offset = 0

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                if self.offset == 0:
                    _dye = dye ^ ((pos.x // 2 + pos.y // 2) % 2 > 0)
                elif self.offset == 1:
                    _dye = dye ^ (((pos.x + 1) // 2 + pos.y // 2) % 2 > 0)
                elif self.offset == 2:
                    _dye = dye ^ ((pos.x // 2 + (pos.y + 1) // 2) % 2 > 0)
                else:
                    _dye = dye ^ (((pos.x + 1)//2 + (pos.y + 1)//2) % 2 > 0)
                board.set_dyed(pos, _dye)
