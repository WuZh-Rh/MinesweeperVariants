from . import AbstractDye

class DyeH(AbstractDye):
    name = "h" # horizontal
    __doc__ = "水平染色"

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
                _dye = dye ^ ((pos.x + self.offset) % 2 > 0)
                board.set_dyed(pos, _dye)
