from minesweepervariants.abs.board import AbstractBoard
from . import AbstractClueSharp

class Rule1L1sharp(AbstractClueSharp):
    name = ["1L1#", "误差 + 标签"]
    doc = ("包含以下规则: [1L], [1L1M], [1L1L], [1L1N], [1L1W], [1L1N], [1L1X], [1L1P], [1L1E]\n"
              "使用[1L1#:]以包括[1L1W]")

    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        rules_name = ["1L", "1L1M", "1L1L", "1L1N", "1L1N", "1L1X", "1L1P", "1L1E"]
        if data is not None:
            rules_name += ["1L1W"]
        super().__init__(rules_name, board, data)
