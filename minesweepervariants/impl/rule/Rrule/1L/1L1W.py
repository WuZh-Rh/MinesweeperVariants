from typing import Dict, Generator

from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractPosition, AbstractBoard
from .....utils.image_create import get_text, get_row, get_col
from .....utils.image_create import get_dummy
from .....utils.tool import get_logger, get_random

from .....utils.web_template import MultiNumber


def liar_1W(values: list[int], _random) -> list[int]:
    if len(values) == 0:
        values = [1]
    elif len(values) == 1:
        values[0] += 1 if _random.random() > 0.5 else -1
        if values[0] > 8:
            values[0] = 7
        if values[0] < 0:
            values[0] = 1
    else:
        # if _random.random() > 0.5: # add 1
        #     idx = _random.randint(0, len(values) - 1)
        #     values[idx] += 1
        # else: # minus 1
        #     non_one_indices = [i for i, v in enumerate(values) if v > 1]
        #     if non_one_indices:
        #         idx = _random.choice(non_one_indices)
        #         values[idx] -= 1
        #     else:
        #         values[0] += 1  # all are 1, just add one

        # only first and last can be liared
        _first = _random.random() > 0.5
        _pos = _random.random() > 0.5

        if _first:
            if not _pos and values[0] > 1:
                values[0] -= 1
            else:
                values[0] += 1
        else:
            if not _pos and values[-1] > 1:
                values[-1] -= 1
            else:
                values[-1] += 1
    
    return values

def unliar_1W(values: list[int]) -> Generator[list[int], None, None]:
    if len(values) == 1:
        if values[0] > 1:
            yield [values[0] - 1]
        if values[0] < 8:
            yield [values[0] + 1]
        else:
            yield [1]
    elif len(values) > 1:
        sum_with_space = sum(values) + len(values) # e.g. 1.2.2 -> 1+2+2+3=8
        if values[0] > 1:
            yield [values[0] - 1] + values[1:]
        if sum_with_space < 8:
            yield [values[0] + 1] + values[1:]
        if values[-1] > 1:
            yield values[:-1] + [values[-1] - 1]
        if sum_with_space < 8:
            yield values[:-1] + [values[-1] + 1]
    else: # should not happen
        yield [1]

def decode(code: bytes) -> list[int]:
    if len(code) == 2:
        if code[1] > 0xf:
            return [code[1] >> 4, code[1] & 0xf, code[0] >> 4, code[0] & 0xf]
        return [code[1] & 0xf, code[0] >> 4, code[0] & 0xf]
    elif len(code) == 1:
        if code[0] > 0xf:
            return [code[0] >> 4, code[0] & 0xf]
        return [code[0] & 0xf]
    return []


def encode(values: list[int]) -> bytes:
    if len(values) == 1:
        return bytes([values[0] & 0xf])

    if len(values) == 2:
        return bytes([(values[0] << 4) | (values[1] & 0xf)])

    if len(values) == 3:
        b0 = ((values[1] & 0xf) << 4) | (values[2] & 0xf)
        b1 = values[0] & 0xf
        return bytes([b0, b1])

    if len(values) == 4:
        b0 = ((values[2] & 0xf) << 4) | (values[3] & 0xf)
        b1 = ((values[0] & 0xf) << 4) | (values[1] & 0xf)
        return bytes([b0, b1])

    return b""


def MineStatus_1W(clue: list) -> list:
    """
    返回值：一个int列表，其中存的每一个int表示：
        一个二进制数，第i位（从低到高）表示从左上角开始顺时针旋转，第i个格子的雷情况（是雷->1，非雷->0）
        将这个二进制数转化为十进制存储到元素当中，如42(10) == 00101010(2)，即这个线索格的右上、右下、左下有雷
    """
    ans = []
    a = [0 for _ in range(8)]  # 决策列表

    def dfs(step: int):
        if step >= 8:  # 最终处理
            # 先写没有剪枝的
            test = []
            last = 0
            for i in range(8):
                if a[i]:
                    last += 1
                else:
                    if last != 0: test.append(last)
                    last = 0
            if last != 0: test.append(last)
            if a[-1] and a[0] and len(test) != 1:
                test[0] += test[-1]
                del test[-1]
            if not test: test = [0]
            test.sort()
            if test != clue: return None
            #
            status = 0
            for i in range(8):
                status += 2 ** i * a[i]
            if status not in ans:
                ans.append(status)
            # if a[:] not in ans:
            #     ans.append(a[:])
            return None
        a[step] = 0
        dfs(step + 1)
        a[step] = 1
        dfs(step + 1)
        return None

    dfs(0)
    return ans

class Rule1L1W(AbstractClueRule):
    name = ["1L1W", "LW", "误差 + 数墙", "Liar + Wall"]
    doc = ""

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        random = get_random()
        for pos, _ in board("N"):
            nei = [pos.right(), pos.right().down(), pos.down(), pos.left().down(),
                   pos.left(), pos.left().up(), pos.up(), pos.right().up()]
            values = []
            nei_type = board.batch(nei, mode="type")
            value = 0
            t = ""
            for t in nei_type:
                if t == "F":
                    value += 1
                elif value != 0:
                    values.append(value)
                    value = 0
            if value != 0 and t == nei_type[0] == "F":
                values[0] += value
            elif value != 0:
                values.append(value)
            
            values = liar_1W(values, random)
            values.sort()

            obj = Value1L1W(pos, encode(values))
            board.set_value(pos, obj)
            logger.debug(f"[1L1W]set {obj} to {pos}")

        return board


class Value1L1W(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.values: list[int] = decode(code)
        self.pos = pos

    def __repr__(self):
        return ".".join([str(i) for i in self.values]) if len(self.values) > 0 else "0"

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.pos.neighbors(2)

    def web_component(self, board) -> Dict:
        if not self.values:
            return MultiNumber([0])
        return MultiNumber(self.values)

    def compose(self, board) -> Dict:
        if len(self.values) <= 1:
            value = 0
            if len(self.values) == 1:
                value = self.values[0]
            return get_col(
                get_dummy(height=0.175),
                get_text(str(value)),
                get_dummy(height=0.175),
            )
        if len(self.values) == 2:
            text_a = get_text(str(self.values[0]))
            text_b = get_text(str(self.values[1]))
            return get_col(
                get_dummy(height=0.175),
                get_row(
                    text_a,
                    text_b
                ),
                get_dummy(height=0.175),
            )
        elif len(self.values) == 3:
            text_a = get_text(str(self.values[0]))
            text_b = get_text(str(self.values[1]))
            text_c = get_text(str(self.values[2]))
            return get_col(
                get_row(
                    text_a,
                    text_b,
                    # spacing=0
                ),
                text_c,
            )
        elif len(self.values) == 4:
            text_a = get_text(str(self.values[0]))
            text_b = get_text(str(self.values[1]))
            text_c = get_text(str(self.values[2]))
            text_d = get_text(str(self.values[3]))
            return get_col(
                get_row(
                    text_a,
                    text_b,
                ),
                get_row(
                    text_c,
                    text_d
                )
            )
        else:
            # 我也不知道为什么会出现>5个数字的情况
            return get_text("")

    @classmethod
    def type(cls) -> bytes:
        return Rule1L1W.name[0].encode("ascii")

    def code(self) -> bytes:
        return encode(self.values)

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        var_list = board.batch([
            self.pos.right(), self.pos.right().down(),
            self.pos.down(), self.pos.left().down(),
            self.pos.left(), self.pos.left().up(),
            self.pos.up(), self.pos.right().up()
        ], mode="variable")

        possible_list = [[]]

        # for value in MineStatus_1W(self.values):
        for raw_values in unliar_1W(self.values):
            for value in MineStatus_1W(raw_values):
                bool_list = [(value >> i) & 1 == 1 for i in reversed(range(8))]
                flag = False
                for index, var in enumerate(var_list):
                    if var is None and bool_list[index]:
                        flag = True
                        break
                    if var is None:
                        continue
                    possible_list[-1].append(bool_list[index])
                if flag:
                    possible_list.pop(-1)
                possible_list.append([])

        if any(v is None for v in var_list):
            var_list = [var for var in var_list if var is not None]
        possible_list.pop(-1)

        if possible_list:
            model.AddAllowedAssignments(var_list, possible_list).OnlyEnforceIf(s)
        else:
            model.Add(sum(var_list) == 0).OnlyEnforceIf(s)
