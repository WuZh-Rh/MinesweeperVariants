from ....utils.tool import get_random

from . import AbstractDye


class DyeR(AbstractDye):
    name = "r" # random
    fullname = "随机染色"

    def __init__(self, args):
        self.percentage = None
        if args:
            self.percentage = int(args) / 100

    def dye(self, board):
        random = get_random()
        if self.percentage:
            positions = [pos for pos, _ in board()]
            positions = random.sample(positions, round(len(positions) * self.percentage))
            for pos in positions:
                board.set_dyed(pos, True)
        else:
            for key in board.get_interactive_keys():
                pos = board.boundary(key=key)
                for pos, _ in board():
                    board.set_dyed(pos, random.random() >= 0.5)