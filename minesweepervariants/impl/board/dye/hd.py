from . import AbstractDye

class DyeHD(AbstractDye):
    name = "hd"
    __doc__ = "水平2x1染色"

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                _dye = dye ^ ((pos.x * 2 + pos.y) % 4 > 1)
                board.set_dyed(pos, _dye)
