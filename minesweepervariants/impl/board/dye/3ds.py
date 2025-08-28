#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/10 09:52
# @Author  : xxx
# @FileName: c.py

from . import AbstractDye


class DyeC(AbstractDye):
    name = "3ds"
    fullname = "3D空心染色"

    def dye(self, board):
        dye = True
        keys = board.get_interactive_keys()
        keys = set(filter(lambda k: k.isdigit(), keys))
        last = max(keys)
        first = min(keys)
        for key in keys:
            boundary = board.boundary(key)
            if key in (first, last):
                continue
            for pos, _ in board(key=key):
                if pos.x == 0 or pos.y == 0 or pos.x == boundary.x or pos.y == boundary.y:
                    continue
                _dye = dye
                board.set_dyed(pos, _dye)
