from . import AbstractDye


class DyeCst(AbstractDye):
    name = "cst"
    fullname = "自定义染色"

    def __init__(self, args: str):
        self.pos = [True if c=='1' else False for c in args if c in "01"]

    def dye(self, board):
        dye = True
        keys = board.get_interactive_keys()
        keys = set(filter(lambda k: k.isdigit(), keys))
        last = max(keys)
        first = min(keys)
        for key in keys:
            for i, (pos, _) in enumerate(board(key=key)):
                try:
                    board.set_dyed(pos, self.pos[i])
                except:
                    raise ValueError("染色失败!")
