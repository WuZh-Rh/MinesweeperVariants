from . import AbstractDye

class DyeSP(AbstractDye):
    name = "sp" # spiral
    __doc__ = "螺旋染色"

    def parse_int(self, str_value, default):
        if str_value is None:
            return default
        try:
            return int(str_value)
        except ValueError:
            return default

    def __init__(self, args):
        # if args:
        #     self.base_color = True
        # else:
        #     self.base_color = False # 背景色是非染色（第一圈染色）

        if not args:
            self.base_color = False # 背景色是非染色（第一圈染色）
            self.clockwise = True # 顺时针
        else:
            all_args = args.split(':')
            self.base_color = (self.parse_int(all_args[0], 0) != 0)
            self.clockwise = True if len(all_args) < 2 else (self.parse_int(all_args[1], 1) != 0)
    
    def dye(self, board):
        dye = self.base_color
        for key in board.get_interactive_keys():
            '''
            5x5: (0,0) (0,1) (0,2) (0,3) (0,4) (1,4) (2,4) (3,4) (3,3) (3,2) (3,1) (2,1) (2,2)
            '''
            n, m = board.get_config(key, 'size')
            for i in range(n):
                for j in range(m):
                    board.set_dyed(board.get_pos(i, j), dye) # 背景色
            dye = not dye # 正色

            top, bottom, left, right = 0, n - 1, 0, m - 1
            while top <= bottom and left <= right:
                if self.clockwise:
                    for j in range(left, right + 1): # (top, left) -> (top, right)
                        board.set_dyed(board.get_pos(top, j), dye)
                    for i in range(top + 1, bottom): # (top+1, right) -> (bottom-1, right)
                        board.set_dyed(board.get_pos(i, right), dye)
                    for j in range(right - 1, left, -1): # (bottom-1, right-1) -> (bottom-1, left+1)
                        board.set_dyed(board.get_pos(bottom-1, j), dye)
                    for i in range(bottom - 2, top + 1, -1): # (bottom-2, left+1) -> (top, left+1)
                        board.set_dyed(board.get_pos(i, left+1), dye)
                else:
                    for i in range(top, bottom + 1):
                        board.set_dyed(board.get_pos(i, left), dye)
                    for j in range(left + 1, right):
                        board.set_dyed(board.get_pos(bottom, j), dye)
                    for i in range(bottom - 1, top, -1):
                        board.set_dyed(board.get_pos(i, right-1), dye)
                    for j in range(right - 2, left + 1, -1):
                        board.set_dyed(board.get_pos(top+1, j), dye)
                top += 2
                bottom -= 2
                left += 2
                right -= 2


