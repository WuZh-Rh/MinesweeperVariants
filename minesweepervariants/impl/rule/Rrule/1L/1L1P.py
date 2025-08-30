from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractPosition, AbstractBoard
from .....utils.tool import get_logger, get_random

def liar_1P(value: int, random) -> int:
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = 1
    if value > 4:
        value = 3
    return value

def unliar_1P(value: int) -> list[int]:
    if value == 0:
        return [1]
    if value == 4:
        return [3]
    return [value - 1, value + 1]

def MineStatus_1P(clue: int) -> list[int]:
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
            if len(test) != clue: return None
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

class Rule1L1P(AbstractClueRule):
    name = ["1L1P", "LP", "误差 + 分组", "Liar + Partition"]
    doc = ""

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        random = get_random()
        for pos, _ in board("N"):
            nei = [pos.right(), pos.right().down(), pos.down(), pos.left().down(),
                   pos.left(), pos.left().up(), pos.up(), pos.right().up()]
            nei_type = board.batch(nei, mode="type")
            value = 0
            _t = ""
            for t in nei_type:
                if t != "F" and _t == "F":
                    value += 1
                _t = t
            if nei_type[-1] == "F" and nei_type[0] != "F":
                value += 1
            
            value = liar_1P(value, random)
            
            obj = Value1L1P(pos, bytes([value]))
            board.set_value(pos, obj)
            logger.debug(f"[1L1P]set {obj} to {pos}")

        return board

class Value1L1P(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.pos = pos

    def __repr__(self):
        return str(self.value)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        return self.pos.neighbors(2)

    @classmethod
    def type(cls) -> bytes:
        return Rule1L1P.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value])

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

        for raw_value in unliar_1P(self.value):
            for value in MineStatus_1P(raw_value):
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

        model.AddAllowedAssignments(var_list, possible_list).OnlyEnforceIf(s)
