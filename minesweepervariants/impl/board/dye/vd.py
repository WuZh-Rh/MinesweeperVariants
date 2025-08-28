from . import AbstractDye

class DyeVD(AbstractDye):
    name = "vd" # vertical dual
    __doc__ = "竖直1x2染色"

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
                _dye = dye ^ ((pos.x + pos.y * 2 + self.offset) % 4 > 1)
                board.set_dyed(pos, _dye)
