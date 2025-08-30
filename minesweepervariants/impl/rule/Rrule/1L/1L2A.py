import itertools
from typing import List, Tuple, Optional

from minesweepervariants.abs.rule import AbstractRule
from .....abs.Rrule import AbstractClueRule, AbstractClueValue
from .....abs.board import AbstractBoard, AbstractPosition

from .....utils.tool import get_logger, get_random

def liar_2A(value: int | None, random) -> int | None:
    if value is None:
        return None
    value += 1 if random.random() > 0.5 else -1
    if value < 0:
        value = 1
    return value

def unliar_2A(value: int | None) -> list[int | None]:
    if value is None:
        return [None]
    res = []
    if value > 0:
        res.append(value - 1)
    res.append(value + 1)
    return res

class Rule1L2A(AbstractClueRule):
    name = ["1L2A", "误差 + 面积", "Liar + Area"]
    doc = ""

    def __init__(self, board: "AbstractBoard" = None, data=None):
        super().__init__(board, data)
        self.flag_1S = None

    def combine(self, rules: List[Tuple['AbstractRule', Optional[str]]]):
        """
        合并规则：
        - 如果存在 (rule, data)，其中 rule 的 name 是 '1S'
        - 并且 data 满足以下之一：
            * None
            * "1"
            * "1;1;...;1"（由一个或多个 '1' 组成，中间以分号分隔）
        则将 self.flag_1S 设为 True。
        """
        for rule, data in rules:
            name = getattr(rule, "name", None)
            if isinstance(name, list):
                name = name[0] if name else None

            if (name in ["1S", "3Y", "1S'", "1S^"] and
               (data is None or all(x == "1" or "1:1" in x for x in data.split(";")))):
                self.flag_1S = True

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        logger = get_logger()
        random = get_random()
        for pos, _ in board("N"):
            if self.flag_1S:
                code = b'\x00\x00' if board.batch(pos.neighbors(1), "type").count("F") > 0 else b'\x01' # 0 liar to 1
                board.set_value(pos, Value1L2A(pos, code))
                continue
            checked = [[False for _ in range(20)] for _ in range(20)]

            def dfs(p: 'AbstractPosition', _checked):
                if not board.in_bounds(p): return None
                if board.get_type(p) != "F": return None
                if _checked[p.x][p.y]: return None
                _checked[p.x][p.y] = True
                dfs(p.left(1), _checked)
                dfs(p.right(1), _checked)
                dfs(p.up(1), _checked)
                dfs(p.down(1), _checked)
                return None

            dfs(pos.left(1), checked)
            dfs(pos.right(1), checked)
            dfs(pos.up(1), checked)
            dfs(pos.down(1), checked)
            cnt = 0
            for i in range(20):
                for j in range(20):
                    if checked[i][j]:
                        cnt += 1
            cnt = liar_2A(cnt, random)
            board.set_value(pos, Value1L2A(pos, bytes([cnt])))
            logger.debug(f"Set {pos} to 1L2A[{cnt}]")
        return board


class Value1L2A(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = None):
        super().__init__(pos, code)
        self.value = code[0] if len(code) == 1 else None
        self.neighbor = pos.neighbors(1)
        self.pos = pos

    def __repr__(self) -> str:
        if self.value is None:
            return ">0"
        return f"{self.value}"

    @classmethod
    def type(cls) -> bytes:
        return Rule1L2A.name[0].encode("ascii")

    def code(self) -> bytes:
        if self.value is None:
            return b'\x00\x00'
        return bytes([self.value])

    def create_constraints(self, board: 'AbstractBoard', switch):
        # 跳过已有的线索格
        model = board.get_model()
        s = switch.get(model, self)

        if self.value is None:
            var_list = board.batch(self.pos.neighbors(1), "var", drop_none=True)
            model.AddBoolOr(var_list).OnlyEnforceIf(s)
            return

        def dfs(
                deep: int,
                valides: list = None,
                locked: list = None  # 上级锁定的格子,不允许进行扩展
        ):
            if valides is None:
                valides = [self.pos]
            if locked is None:
                locked = []
            checked = set()
            for pos in valides:
                for _pos in pos.neighbors(1):
                    if _pos in locked:
                        continue
                    if _pos in valides:
                        continue
                    if not board.in_bounds(_pos):
                        continue
                    checked.add(_pos)
            if deep == 0:
                if "F" not in board.batch(list(checked), "type"):
                    yield valides, list(checked) + locked
            else:
                for n in range(1, min(deep, len(checked)) + 1):
                    for combo in itertools.combinations(checked, n):
                        outside = [pos for pos in checked if pos not in combo]
                        if "C" in board.batch(combo, "type"):
                            continue
                        if "F" in board.batch(outside, "type"):
                            continue
                        yield from dfs(deep - n, valides + list(combo), locked + outside)

        tmp_list = []
        for raw_value in unliar_2A(self.value):
            for vars_f, vars_t in dfs(raw_value):
                vars_f = [var_f for var_f in vars_f if var_f != self.pos]
                tmp = model.NewBoolVar(f"tmp,F:{vars_f}|C:{vars_t}")
                vars_t = board.batch(vars_t, mode="variable")
                vars_f = board.batch(vars_f, mode="variable")
                model.Add(sum(vars_t) == 0).OnlyEnforceIf(tmp)
                if vars_f:
                    model.AddBoolAnd(vars_f).OnlyEnforceIf(tmp)
                tmp_list.append(tmp)
        model.AddBoolOr(tmp_list).OnlyEnforceIf(s)
        get_logger().trace(f"position:{self.pos}, value:{self}, 枚举所有可能性共:{len(tmp_list)}个")

