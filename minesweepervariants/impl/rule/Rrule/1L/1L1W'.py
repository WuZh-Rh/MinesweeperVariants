from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition
from .....utils.tool import get_logger, get_random

def liar_1Wp(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = 1
    if value > 8:
        value = 7
    return value

def unliar_1Wp(value: int) -> list[int]:
    if value == 0:
        return [1]
    if value == 8:
        return [7]
    return [value - 1, value + 1]

def MineStatus_1W(clue: list) -> list[int]:
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

class Rule1L1Wp(AbstractClueRule):
    name = ["1L1W'", "LW'", "误差 + 最长数墙", "Liar + Longest Wall"]
    doc = ""

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        for pos, _ in board("N"):
            pos_list = [pos.right(), pos.right().down(), pos.down(), pos.left().down(),
                        pos.left(), pos.left().up(), pos.up(), pos.right().up()] * 2
            value = 0
            tmp = 0
            for _pos in pos_list:
                if board.get_type(_pos) == "F":
                    tmp += 1
                elif tmp != 0:
                    value = max(value, tmp)
                    tmp = 0
            if tmp > 8:
                value = 8
            value = liar_1Wp(value, get_random())
            obj = Value1L1Wp(pos, bytes([value]))
            board[pos] = obj
        return board

class Value1L1Wp(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.pos = pos

    def __repr__(self) -> str:
        return str(self.value)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.pos.neighbors(2)

    @classmethod
    def type(cls) -> bytes:
        return Rule1L1Wp.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard', switch):

        def get_values(_value: int, _length=3):
            if _length <= 0:
                yield []
            if _value == 0:
                return []
            if _length > 0:
                for i in range(_value):
                    for j in get_values(i + 1, _length - 1):
                        yield [i + 1] + j

        model = board.get_model()
        s = switch.get(model, self)

        var_list = board.batch([
            self.pos.right(), self.pos.right().down(),
            self.pos.down(), self.pos.left().down(),
            self.pos.left(), self.pos.left().up(),
            self.pos.up(), self.pos.right().up()
        ], mode="variable")

        possible_list = [[]]
        values = []

        for raw_value in unliar_1Wp(self.value):
            for length in range(3 - raw_value // 2):
                if length == 0:
                    values.extend(MineStatus_1W([raw_value]))
                for k in get_values(3, _length=length + 1):
                    values.extend(MineStatus_1W(([raw_value] + k)[::-1]))

        for value in values:
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
