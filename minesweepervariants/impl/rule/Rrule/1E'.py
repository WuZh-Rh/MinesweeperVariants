#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
[1E'] 视差 (Eyesight')：线索表示纵向和横向的视野之差，箭头指示视野更长的方向
"""
from typing import Dict

from minesweepervariants.utils.web_template import Number, StrWithArrow
from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition

from ....utils.image_create import get_image, get_text, get_row, get_col, get_dummy


class Rule1E(AbstractClueRule):
    name = ["1E'", "E'", "视差", "Eyesight'"]
    doc = "线索表示纵向和横向的视野之差，箭头指示视野更长的方向"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        for pos, _ in board("N"):
            value = 0
            # 四方向的函数
            direction_funcs = [
                lambda _n: type(pos)(pos.x + _n, pos.y, pos.board_key),  # 右
                lambda _n: type(pos)(pos.x - _n, pos.y, pos.board_key),  # 左
                lambda _n: type(pos)(pos.x, pos.y + _n, pos.board_key),  # 上
                lambda _n: type(pos)(pos.x, pos.y - _n, pos.board_key)   # 下
            ]

            for fn in direction_funcs[:2]:  # 只计算横向
                n = 1
                while True:
                    next_pos = fn(n)
                    if not board.in_bounds(next_pos):
                        break
                    if board.get_type(next_pos) == "F":  # 遇到雷，视线被阻挡
                        break
                    value += 1
                    n += 1

            for fn in direction_funcs[2:]:  # 只计算纵向
                n = 1
                while True:
                    next_pos = fn(n)
                    if not board.in_bounds(next_pos):
                        break
                    if board.get_type(next_pos) == "F":  # 遇到雷，视线被阻挡
                        break
                    value -= 1
                    n += 1

            obj = Value1E(pos, bytes([value + 128]))
            board.set_value(pos, obj)
        return board


class Value1E(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        self.value = code[0]
        self.value = self.value - 128
        self.pos = pos

    def __repr__(self):
        return str(self.value)

    def high_light(self, board: 'AbstractBoard') -> list['AbstractPosition']:
        positions = []
        for i in [
            (1, 0), (-1, 0),
            (0, 1), (0, -1),
        ]:
            n = 0
            while board.get_type(pos := self.pos.shift(i[0] * n, i[1] * n)) not in "F":
                n += 1
                positions.append(pos)
        return positions

    @classmethod
    def type(cls) -> bytes:
        return Rule1E.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.value+128])

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)

        direction_funcs = [
            lambda n: type(self.pos)(self.pos.x + n, self.pos.y, self.pos.board_key),  # 右
            lambda n: type(self.pos)(self.pos.x - n, self.pos.y, self.pos.board_key),  # 左
            lambda n: type(self.pos)(self.pos.x, self.pos.y + n, self.pos.board_key),  # 上
            lambda n: type(self.pos)(self.pos.x, self.pos.y - n, self.pos.board_key)   # 下
        ]

        def max_steps(fn):
            n = 1
            while True:
                p = fn(n)
                if not board.in_bounds(p):
                    return n - 1
                if board.get_variable(p) is None:
                    return n - 1
                n += 1

        def collect_dir(fn, steps):
            _t_positions = []
            if steps == 0:
                p_block = fn(1)
                f_var = board.get_variable(p_block) if board.in_bounds(p_block) else None
                return _t_positions, f_var, True

            for k in range(1, steps + 1):
                p = fn(k)
                if not board.in_bounds(p):
                    return [], None, False
                var = board.get_variable(p)
                if var is None:
                    return [], None, False
                _t_positions.append(p)

            p_block = fn(steps + 1)
            f_var = board.get_variable(p_block) if board.in_bounds(p_block) else None
            return _t_positions, f_var, True

        max_right = max_steps(direction_funcs[0])
        max_left = max_steps(direction_funcs[1])
        max_up = max_steps(direction_funcs[2])
        max_down = max_steps(direction_funcs[3])

        possible_list = []  # 每项 (set_of_T_positions, list_of_F_vars_or_None)

        max_steps_list = [max_right, max_left, max_up, max_down]

        possible_list = []

        def enum_counts(idx: int, counts: list[int], accum_T: list, accum_F: list):
            # 计算当前已确定的 delta 与剩余方向的可达范围
            current_delta = (counts[0] + counts[1]) - (counts[2] + counts[3])
            # 计算剩余最大可增加的横向与纵向
            horiz_remain = 0
            vert_remain = 0
            for j in range(idx, 4):
                if j < 2:
                    horiz_remain += max_steps_list[j]
                else:
                    vert_remain += max_steps_list[j]

            min_possible = current_delta - vert_remain
            max_possible = current_delta + horiz_remain
            if not (min_possible <= self.value <= max_possible):
                return

            if idx == 4:
                if (counts[0] + counts[1]) - (counts[2] + counts[3]) == self.value:
                    # 复制 accum_F，因为里面可能包含 None
                    possible_list.append((set(accum_T), list(accum_F)))
                return

            fn = direction_funcs[idx]
            max_n = max_steps_list[idx]
            for steps in range(0, max_n + 1):
                t_pos, f_var, ok = collect_dir(fn, steps)
                if not ok:
                    continue

                # push
                added = len(t_pos)
                accum_T.extend(t_pos)
                accum_F.append(f_var)
                counts[idx] = steps

                enum_counts(idx + 1, counts, accum_T, accum_F)

                # pop
                for _ in range(added):
                    accum_T.pop()
                accum_F.pop()
                counts[idx] = 0

        enum_counts(0, [0, 0, 0, 0], [], [])

        tmp_list = []
        for t_positions, f_vars in possible_list:
            vars_t = board.batch(t_positions, mode="variable") if t_positions else []
            vars_f = [v for v in f_vars if v is not None]

            tmp = model.NewBoolVar(f"tmp_1E_{self.pos.x}_{self.pos.y}_{len(tmp_list)}")
            # 当 tmp 和 线索开关 s 同时成立时，T 位置均为非雷（sum == 0）
            model.Add(sum(vars_t) == 0).OnlyEnforceIf([tmp, s])
            # 阻挡位置（若有变量）全部为雷
            if vars_f:
                model.AddBoolAnd(vars_f).OnlyEnforceIf([tmp, s])
            tmp_list.append(tmp)

        if tmp_list:
            model.AddBoolOr(tmp_list).OnlyEnforceIf(s)

    def web_component(self, board) -> Dict:
        if self.value == 0:
            return Number(0)
        if self.value < 0:
            return get_col(
                get_image(
                    "double_arrow",
                    image_height=0.4,
                ),
                get_dummy(height=-0.1),
                get_text(str(-self.value))
            )
        if self.value > 0:
            return get_row(
                get_dummy(width=0.15),
                get_image(
                    "double_arrow",
                    style="transform: rotate(90deg);"
                ),
                get_dummy(width=-0.15),
                get_text(str(self.value)),
                get_dummy(width=0.15),
            )
    def web_component(self, board) -> Dict:
        if self.value == 0:
            return Number(0)
        if self.value < 0:
            return StrWithArrow(str(-self.value), "left_right")
        if self.value > 0:
            return StrWithArrow(str(self.value), "up_down")


    def compose(self, board):
        if self.value == 0:
            return super().compose(board)
        if self.value < 0:
            return get_col(
                get_image(
                    "double_horizontal_arrow",
                    image_height=0.4,
                ),
                get_dummy(height=-0.1),
                get_text(str(-self.value))
            )
        if self.value > 0:
            return get_row(
                    get_dummy(width=0.15),
                    get_image("double_vertical_arrow", ),
                    get_dummy(width=-0.15),
                    get_text(str(self.value)),
                    get_dummy(width=0.15),
            )
