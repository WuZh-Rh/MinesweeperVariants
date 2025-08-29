from ....utils.tool import get_random

from . import AbstractDye


class DyeR(AbstractDye):
    name = "r" # random
    fullname = "随机染色"

    def __init__(self, args: str):
        self.percentage = None
        self.count = None
        match args:
            case str(x) if x.endswith('%') and x[:-1].isdigit():
                self.percentage = int(x[:-1]) / 100
            case str(x) if x.isdigit():
                self.count = int(x)


    def dye(self, board):
        random = get_random()
        if self.count:
            positions = [pos for pos, _ in board()]
            positions = random.sample(positions, self.count)
            for pos in positions:
                board.set_dyed(pos, True)
        elif self.percentage:
            positions = [pos for pos, _ in board()]
            positions = random.sample(positions, round(len(positions) * self.percentage))
            for pos in positions:
                board.set_dyed(pos, True)
        else:
            for key in board.get_interactive_keys():
                pos = board.boundary(key=key)
                for pos, _ in board():
                    board.set_dyed(pos, random.random() >= 0.5)