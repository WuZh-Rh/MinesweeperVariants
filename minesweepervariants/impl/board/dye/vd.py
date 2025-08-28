from . import AbstractDye

class DyeVD(AbstractDye):
    name = "vd"
    __doc__ = "垂直1x2染色"

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                _dye = dye ^ ((pos.x + pos.y * 2) % 4 > 1)
                board.set_dyed(pos, _dye)
