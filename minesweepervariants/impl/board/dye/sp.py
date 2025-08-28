from . import AbstractDye

class DyeSP(AbstractDye):
    name = "sp" # spiral
    __doc__ = "螺旋染色"

    def __init__(self, args):
        if args:
            self.base_color = True
        else:
            self.base_color = False # 背景色是非染色（第一圈染色）
    
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
                for j in range(left, right + 1): # (top, left) -> (top, right)
                    print('PATH 1', top, j)
                    board.set_dyed(board.get_pos(top, j), dye)
                for i in range(top + 1, bottom): # (top+1, right) -> (bottom-1, right)
                    print('PATH 2', i, right)
                    board.set_dyed(board.get_pos(i, right), dye)
                for j in range(right - 1, left, -1): # (bottom-1, right-1) -> (bottom-1, left+1)
                    print('PATH 3', bottom-1, j)
                    board.set_dyed(board.get_pos(bottom-1, j), dye)
                for i in range(bottom - 2, top + 1, -1): # (bottom-2, left+1) -> (top, left+1)
                    print('PATH 4', i, left)
                    board.set_dyed(board.get_pos(i, left+1), dye)
                top += 2
                bottom -= 2
                left += 2
                right -= 2


