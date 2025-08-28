from . import AbstractDye

class DyeHD(AbstractDye):
    name = "hd" # horizontal dual
    __doc__ = "水平2x1染色"

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
                _dye = dye ^ ((pos.x * 2 + pos.y + self.offset) % 4 > 1)
                board.set_dyed(pos, _dye)
