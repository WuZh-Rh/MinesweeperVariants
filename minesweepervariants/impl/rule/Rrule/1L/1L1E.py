from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition
from .....utils.tool import get_random

def liar_1E(value: int, random, sizx: int, sizy: int) -> int:
    max_eyesight = sizx + sizy - 1
    value += 1 if random.random() > 0.5 else -1
    if value < 1:
        value += 2
    if value > max_eyesight:
        value -= 2
    return value

def unliar_1E(value: int, sizx: int, sizy: int) -> list[int]:
    if value <= 1:
        return [2]
    if value >= sizx + sizy - 1:
        return [sizx + sizy - 2]
    return [value - 1, value + 1]

class Rule1L1E(AbstractClueRule):
    name = ["1L1E", "LE", "误差 + 视野", "Liar + Eyesight"]
    doc = ""

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        sizx, sizy = board.get_config("1", "size")
        for pos, _ in board("N"):
            value = 1  # 包括自身
            # 四方向的函数
            direction_funcs = [
                lambda _n: type(pos)(pos.x + _n, pos.y, pos.board_key),  # 右
                lambda _n: type(pos)(pos.x - _n, pos.y, pos.board_key),  # 左
                lambda _n: type(pos)(pos.x, pos.y + _n, pos.board_key),  # 上
                lambda _n: type(pos)(pos.x, pos.y - _n, pos.board_key)   # 下
            ]

            for fn in direction_funcs:
                n = 1
                while True:
                    next_pos = fn(n)
                    if not board.in_bounds(next_pos):
                        break
                    if board.get_type(next_pos) == "F":  # 遇到雷，视线被阻挡
                        break
                    value += 1
                    n += 1
            
            
            value = liar_1E(value, random, sizx, sizy)

            obj = Value1E(pos, bytes([value]))
            board.set_value(pos, obj)
        return board


class Value1E(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.pos = pos

    def __repr__(self):
        return str(self.value)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        positions = []
        for i in [
            (1, 0), (0, 1),
            (-1, 0), (0, -1),
        ]:
            n = 0
            while board.get_type(pos := self.pos.shift(i[0] * n, i[1] * n)) not in "F":
                n += 1
                positions.append(pos)
        return positions

    @classmethod
    def type(cls) -> bytes:
        return Rule1L1E.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard', switch):
        def dfs(value: int, index=0, info: dict = None):
            if info is None:
                info = {"T": [], "F": []}
            if index == 4:
                if value == 1:
                    possible_list.append((set(info["T"]), [var for var in info["F"] if var is not None]))
                return

            # 四方向的函数
            direction_funcs = [
                lambda n: type(self.pos)(self.pos.x + n, self.pos.y, self.pos.board_key),  # 右
                lambda n: type(self.pos)(self.pos.x - n, self.pos.y, self.pos.board_key),  # 左
                lambda n: type(self.pos)(self.pos.x, self.pos.y + n, self.pos.board_key),  # 上
                lambda n: type(self.pos)(self.pos.x, self.pos.y - n, self.pos.board_key)   # 下
            ]

            fn = direction_funcs[index]

            for i in range(value):
                current_pos = fn(i)
                if not board.in_bounds(current_pos):
                    dfs(value - i, index + 1, info)
                    break

                _var_t = board.get_variable(current_pos)
                if _var_t is None:
                    dfs(value - i, index + 1, info)
                    break

                next_pos = fn(i + 1)
                _var_f = board.get_variable(next_pos) if board.in_bounds(next_pos) else None

                info["T"].append(_var_t)
                info["F"].append(_var_f)
                dfs(value - i, index + 1, info)
                info["F"].pop(-1)

            for i in range(value):
                current_pos = fn(i)
                if not board.in_bounds(current_pos):
                    break
                if board.get_variable(current_pos) is None:
                    continue
                info["T"].pop(-1)

        model = board.get_model()
        s = switch.get(model, self)
        possible_list = []

        sizx, sizy = board.get_config("1", "size")
        tmp_list = []
        for raw_value in unliar_1E(self.value, sizx, sizy):
            dfs(value=raw_value)

            for vars_t, vars_f in possible_list:
                tmp = model.NewBoolVar("tmp")
                model.Add(sum(vars_t) == 0).OnlyEnforceIf(tmp)
                if vars_f and any(var is not None for var in vars_f):
                    model.AddBoolAnd([var for var in vars_f if var is not None]).OnlyEnforceIf(tmp)
                tmp_list.append(tmp)

        if tmp_list:
            model.AddBoolOr(tmp_list).OnlyEnforceIf(s)
