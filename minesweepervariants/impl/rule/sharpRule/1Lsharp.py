from minesweepervariants.abs.board import AbstractBoard
from . import AbstractClueSharp

class Rule1Lsharp(AbstractClueSharp):
    name = ["1L#", "误差 + 标签"]
    doc = ("包含以下规则:[1L], [1L1M], [1L1L], [1L1N], [1L1W], [1L1N], [1L1X], [1L1P], [1L1E],"
              "[1L2X], [1L2D], [1L2M], [1L2A]"
              "使用[1L#:]以去除2A(推荐)")
        
    def __init__(self, board: "AbstractBoard" = None, data=None) -> None:
        rules_name = ["1L", "1L1M", "1L1L", "1L1N", "1L1W", "1L1N", "1L1X", "1L1P", "1L1E",
                      "1L2X", "1L2D", "1L2M"]
        if data is None:
            rules_name += ["1L2A"]
        super().__init__(rules_name, board, data)
