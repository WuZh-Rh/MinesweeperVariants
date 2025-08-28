from . import AbstractDye

class DyeW(AbstractDye):
    name = "w" # wrapsaround
    __doc__ = "回环染色"

    def __init__(self, args):
        if args:
            self.base_color = False
        else:
            self.base_color = True # 最外圈染色
    
    def dye(self, board):
        dye = self.base_color
        for key in board.get_interactive_keys():
            n, m = board.get_config(key, 'size')
            _dye = dye

            layers = (min(n, m) + 1) // 2
            for layer in range(layers):
                top, bottom = layer, n - layer - 1
                left, right = layer, m - layer - 1
                if top < bottom:
                    # top row
                    for j in range(left, right + 1):
                        board.set_dyed(board.get_pos(top, j), _dye)
                    # bottom row
                    for j in range(left, right + 1):
                        board.set_dyed(board.get_pos(bottom, j), _dye)
                if left < right:
                    # left column
                    for i in range(top, bottom + 1):
                        board.set_dyed(board.get_pos(i, left), _dye)
                    # right column
                    for i in range(top, bottom + 1):
                        board.set_dyed(board.get_pos(i, right), _dye)
                # 中心格
                if top == bottom and left == right:
                    board.set_dyed(board.get_pos(top, left), _dye)
                _dye = not _dye
