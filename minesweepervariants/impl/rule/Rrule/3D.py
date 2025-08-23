"""
[3D] 辞典：所有雷从左到右，从上到下依次标号。线索表示周围八格的雷的标号之和
"""

from ....abs.board import AbstractBoard, AbstractPosition
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....utils.tool import get_logger
from ....utils.impl_obj import VALUE_QUESS, MINES_TAG


def encode_int_7bit(n: int) -> bytes:
    # 编码主体：每7位 -> 1字节（bit6~bit0，bit7=0）
    if n == 0:
        return b'\x00'
    payload = []

    while n > 0:
        payload.append(n & 0x7f)
        n >>= 7

    return bytes(payload)


def decode_bytes_7bit(data: bytes) -> int:
    if len(data) == 0:
        return 0

    result = 0
    for i in data[::-1]:
        result <<= 7
        result |= i

    return result


class Rule3D(AbstractClueRule):
    name = ["3D", "辞典", "Dict"]
    doc = "所有雷从左到右，从上到下依次标号。线索表示周围八格的雷的标号之和"

    def fill(self, board: AbstractBoard) -> AbstractBoard:
        logger = get_logger()
        for key in board.get_interactive_keys():
            dict = {}
            x = board.boundary(key).x + 1
            y = board.boundary(key).y + 1
            for i in range(x):
                for j in range(y):
                    pos = board.get_pos(i, j, key)
                    if board.get_type(pos) == "F":
                        dict[pos] = len(dict) + 1
            if not dict:
                logger.error(f"[3D] R = 0")
                return board
            for pos, _ in board("N", key=key):
                value = 0
                for nei in pos.neighbors(2):
                    if board.get_type(nei) == "F":
                        value += dict[nei]
                board.set_value(pos, Value3D(pos, code=encode_int_7bit(value)))
                logger.debug(f"[3D] put {value} to {pos}")
        return board


class Value3D(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        self.value = decode_bytes_7bit(code)
        self.neighbors = pos.neighbors(2)

    def __repr__(self) -> str:
        return f"{self.value}"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.neighbors

    @classmethod
    def type(cls) -> bytes:
        return Rule3D.name[0].encode("ascii")

    def code(self) -> bytes:
        return encode_int_7bit(self.value)

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        x = board.boundary(self.pos.board_key).x + 1
        y = board.boundary(self.pos.board_key).y + 1
        N = x * y
        m = [board.get_variable(board.get_pos(i, j, self.pos.board_key)) for i in range(x) for j in range(y)]      # 雷格变量
        P = [model.NewIntVar(0, N, f"[3D]P{i}") for i in range(N)]                                                 # 前缀雷计数
        L = [model.NewIntVar(0, N, f"[3D]L{i}") for i in range(N)]                                                 # 该格的雷编号，非雷为 0

        # 连接 P 与 m（P 是 m 的前缀和）
        # P[0] = m[0]; P[i] = P[i-1] + m[i]
        model.Add(P[0] == m[0]).OnlyEnforceIf(s)
        for i in range(1, N):
            model.Add(P[i] == P[i-1] + m[i]).OnlyEnforceIf(s)

        # 若 m[i]=1，则 L[i]=P[i]；若 m[i]=0，则 L[i]=0
        for i in range(N):
            model.Add(L[i] == P[i]).OnlyEnforceIf([m[i], s])
            model.Add(L[i] == 0).OnlyEnforceIf([m[i].Not(), s])

        model.Add(sum(L[nei.x * y + nei.y] for nei in self.neighbors if board.in_bounds(nei)) == self.value).OnlyEnforceIf(s)
