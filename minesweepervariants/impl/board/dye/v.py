from . import AbstractDye


class DyeC(AbstractDye):
    name = "v"
    __doc__ = "竖直染色"

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                _dye = dye ^ (pos.y % 2 > 0)
                board.set_dyed(pos, _dye)
