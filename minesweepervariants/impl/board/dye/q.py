#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 09:52
# @Author  : xxx
# @FileName: c.py

from . import AbstractDye


class DyeC(AbstractDye):
    name = "q" # quadrant
    __doc__ = "2x2棋盘格染色"

    def parse_int(self, str_value, default):
        if str_value is None:
            return default
        try:
            return int(str_value)
        except ValueError:
            return default

    def __init__(self, args):
        '''
        args: size:dx:dy
        size: 棋盘格大小，默认2
        dx, dy: 棋盘格偏移，默认0
        '''
        if not args:
            self.size = 2
            self.dx = 0
            self.dy = 0
        else:
            all_args = args.split(':')
            self.size = self.parse_int(all_args[0], 2)
            self.dx = self.parse_int(all_args[1], 0) if len(all_args) > 1 else 0
            self.dy = self.parse_int(all_args[2], 0) if len(all_args) > 2 else 0

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                # if self.offset == 0:
                #     _dye = dye ^ ((pos.x // 2 + pos.y // 2) % 2 > 0)
                # elif self.offset == 1:
                #     _dye = dye ^ (((pos.x + 1) // 2 + pos.y // 2) % 2 > 0)
                # elif self.offset == 2:
                #     _dye = dye ^ ((pos.x // 2 + (pos.y + 1) // 2) % 2 > 0)
                # else:
                #     _dye = dye ^ (((pos.x + 1)//2 + (pos.y + 1)//2) % 2 > 0)
                _dye = dye ^ (((pos.x + self.dx) // self.size + (pos.y + self.dy) // self.size) % 2 > 0)
                board.set_dyed(pos, _dye)
