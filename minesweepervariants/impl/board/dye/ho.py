from . import AbstractDye

class DyeHO(AbstractDye):
    name = "ho"
    __doc__ = "水平染色"

    def dye(self, board):
        dye = True
        for key in board.get_interactive_keys():
            dye = not dye
            for pos, _ in board(key=key):
                _dye = dye ^ (pos.x % 2 > 0)
                board.set_dyed(pos, _dye)
