#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/09 11:37
# @Author  : xxx
# @FileName: 3A.py
"""
[3A]兰顿蚂蚁: 数字表示兰顿蚂蚁从线索格出发直至走出题板外所移动的次数。
箭头表示兰顿蚂蚁的初始方向，经过非雷格顺时针旋转90度(右转)，经过雷格逆时针旋转90度(左转)。
数字可以为无穷,其表示当前路径构成了循环
"""
from typing import List, Dict

from minesweepervariants.utils.web_template import StrWithArrow

from ....abs.Rrule import AbstractClueRule, AbstractClueValue
from ....abs.board import AbstractBoard, AbstractPosition
from ....utils.image_create import get_image, get_text, get_row, get_col, get_dummy
from ....utils.impl_obj import MINES_TAG, VALUE_QUESS
from ....utils.tool import get_random


def put(board, pos: 'AbstractPosition', path):
    value = 0
    while board.in_bounds(pos):
        value += 1
        if board.get_type(pos) == "F":
            path += 1
            path %= 4
        else:
            obj = board.get_value(pos)
            obj.append((value, path))
            path += 3
            path %= 4
        # 0.上 1.右 2.下 3.左
        match path:
            case 0:
                pos = pos.down()
            case 1:
                pos = pos.left()
            case 2:
                pos = pos.up()
            case 3:
                pos = pos.right()


class Rule3A(AbstractClueRule):
    name = ["3A", "兰顿蚂蚁"]
    doc = "数字表示兰顿蚂蚁从线索格出发直至走出题板外所移动的次数。"

    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        random = get_random()
        for pos, _ in board("N"):
            board.set_value(pos, Value3A(pos))
        lines = [
            board.get_row_pos(board.get_pos(0, 0)),
            board.get_col_pos(board.get_pos(-1, -1)),
            board.get_row_pos(board.get_pos(-1, -1)),
            board.get_col_pos(board.get_pos(0, 0)),
        ]
        for index in range(4):
            line = lines[index]
            for pos in line:
                put(board, pos, index)
                # print(pos, index)
                # print(board.show_board())
        for _, obj in board("C"):
            obj.end(random.random())
        return board


class Value3A(AbstractClueValue):
    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)
        if not code:
            self.value = 0
            self.dir = 0
            self.data = []
            return
        self.value = code[1]  # 路径长
        self.dir = code[0]  # 0.上 1.右 2.下 3.左

    def __str__(self) -> str:
        return f"{self.value}{'↑→↓←'[self.dir]}"

    def __repr__(self) -> str:
        return f"{self.value}{'^>v<'[self.dir]}"

    def web_component(self, board) -> Dict:
        return StrWithArrow(str(self.value), ["up", "right", "down", "left"][self.dir])

    def compose(self, board) -> Dict:
        match self.dir:
            case 0:
                # 上 ↑ ^
                if self.value == 1:
                    return get_row(
                            get_dummy(width=0.175),
                            get_text("1"),
                            get_image("up"),
                            get_dummy(width=0.175),
                        )
                return get_row(
                        get_text(str(self.value)),
                        get_image("up"),
                        spacing=-0.1,
                    )
            case 1:
                # 右 → >
                return get_col(
                    get_dummy(height=0.1),
                    get_image(
                        "right",
                        image_height=0.2,
                        image_width=0.7
                    ),
                    get_dummy(height=-0.05),
                    get_text(str(self.value)),
                    get_dummy(height=0.2)
                )
            case 2:
                # 下 ↓ V
                if self.value == 1:
                    return get_row(
                            get_dummy(width=0.175),
                            get_text("1"),
                            get_image("down"),
                            get_dummy(width=0.175),
                        )
                return get_row(
                        get_text(str(self.value)),
                        get_image("down"),
                        spacing=-0.1,
                    )
            case 3:
                # 左 ← <
                return get_col(
                    get_dummy(height=0.1),
                    get_image(
                        "left",
                        image_height=0.2,
                        image_width=0.7
                    ),
                    get_dummy(height=-0.05),
                    get_text(str(self.value)),
                    get_dummy(height=0.2)
                )
        return get_text("")

    def high_light(self, board: 'AbstractBoard') -> List['AbstractPosition']:
        pos = self.pos.clone()
        path = (self.dir + 1) % 4
        position = []
        value = float("inf") if self.value == 0 else self.value
        while True:
            if not board.in_bounds(pos):
                break
            if board.get_type(pos) == "N":
                position.append(pos)
                break
            position.append(pos)
            # 0.上 1.右 2.下 3.左
            if board.get_type(pos) == "F":
                path += 3
                path %= 4
            else:
                path += 1
                path %= 4
            match path:
                case 0:
                    pos = pos.down()
                case 1:
                    pos = pos.left()
                case 2:
                    pos = pos.up()
                case 3:
                    pos = pos.right()
            if (
                pos == self.pos and
                path == (self.dir + 1) % 4
            ):
                break
            value -= 1
            if value == 0:
                break
        # print(self.value, position)
        return position

    def append(self, data):
        self.data.append(data)

    def end(self, rand: float):
        if len(self.data) == 0:
            self.dir = int(rand * 4)
            return

        self.data.sort(key=lambda x: x[0])
        self.data: list[tuple[int, int]]

        # 提取所有首个int值
        values = [item[0] for item in self.data]

        # 计算权重 (n_i^2) 和总权重
        weights = [n ** 2 for n in values]
        total_weight = sum(weights)

        # 构建累积概率分布
        cumulative = 0.0
        for i, weight in enumerate(weights):
            prob = weight / total_weight  # 当前元素的概率
            cumulative += prob  # 累积概率
            # 如果 rand 小于当前累积概率，选择当前元素
            if rand < cumulative:
                self.value, self.dir = self.data[i]
                self.data = None
                break

        if self.data is not None:
            self.value, self.dir = self.data[-1]
        del self.data

    @classmethod
    def type(cls) -> bytes:
        return Rule3A.name[0].encode("ascii")

    def code(self) -> bytes:
        return bytes([self.dir, self.value])

    def bfs_get_states(self, board: 'AbstractBoard') -> List[dict]:
        """
        大致思路:
        从方向开始走 如果提前走出边境或者循环就直接丢弃 如果刚好在值内就记录

        一层具象
        从当前位置为根节点构建一棵二叉树进行遍历
        如果说value==-1 那么需要进入while遍历并把所有走出题板的节点删除
        如果value>=1 那么就使用range()

        二层具象
        如果值为无穷 那么需要使用快慢节点进行遍历 一旦重合就立刻将其值放入list
        可能会遇到重复的pos节点 在遍历的时候需要边查表边遍历
        如果出现过就需要直接赋值而不是继续分叉

        三层具象
        针对>=1可以使用ab_bfs列表 对当前abfs进行遍历
        如果出现超出题板 那么就丢出
        如果出现循环 不用管 等时间到了他就死了
        每次创建叉的时候需要查看当前经过的路径是否遍历过

        >=1:
            需要附带的信息有 当前节点, 当前方向, 遍历过的路径的对应值
            具体步骤为:
                沿着当前方向走一步
                查看当前节点有没有超出题板内
                    超出题板就撇了
                查看当前节点在不在对应值列表里面
                    不在就加入对应值列表
                加入b_bfs
        """

        def move(_pos, _dir):
            match _dir:
                case 0:
                    _pos = _pos.up()
                case 1:
                    _pos = _pos.right()
                case 2:
                    _pos = _pos.down()
                case 3:
                    _pos = _pos.left()
            return _pos

        def node(_pos, _dt, _value_map):
            result = []
            if _pos in _value_map:
                # 如果在就继续走
                result.append((_pos, (_dt + _value_map[_pos] * 2 + 1) % 4, _value_map.copy()))
            else:
                if (pos_type := board.get_type(_pos)) != "N":
                    # 当前位置是有值的 直接拿了用
                    _value_map = _value_map.copy()
                    _value_map[_pos] = 0 if pos_type == "C" else 1
                    result.append((_pos, (_dt + _value_map[_pos] * 2 + 1) % 4, _value_map))
                else:
                    # 如果不在说明未经过过该节点 就加入map
                    _value_map_a = _value_map.copy()
                    _value_map_b = _value_map.copy()
                    _value_map_a[_pos] = 1
                    _value_map_b[_pos] = 0
                    result.extend([
                        (_pos, (_dt + 3) % 4, _value_map_a),
                        (_pos, (_dt + 1) % 4, _value_map_b),
                    ])
            return result

        root = self.pos.clone()
        a_bfs = [(root, self.dir, {root.clone(): 0})]
        b_bfs = []
        answer_list = []

        if self.value == 0:
            flag = False
            # 处理循环的情况
            while len(a_bfs) > 0:
                for pos, dt, value_map in a_bfs:
                    if flag and pos == self.pos and dt == self.dir:
                        # 如果当前位置和方向和自身完全相同 就说明循环了
                        answer_list.append(value_map)
                        continue
                    # 沿着当前方向走一步
                    # 0.上 1.右 2.下 3.左
                    pos = move(pos, dt)
                    if not board.in_bounds(pos):
                        # 查看当前节点有没有超出题板内
                        continue
                    b_bfs.extend(node(pos, dt, value_map))
                a_bfs = b_bfs
                b_bfs = []
                flag = True
            return answer_list
        else:
            for depth in range(self.value, 0, -1):
                for pos, dt, value_map in a_bfs:
                    # 沿着当前方向走一步
                    # 0.上 1.右 2.下 3.左
                    pos = move(pos, dt)
                    # 查看当前节点有没有超出题板内
                    if not board.in_bounds(pos):
                        # 如果depth==self.value就是要的这个结果
                        if depth == 1:
                            answer_list.append(value_map)
                        continue
                    b_bfs.extend(node(pos, dt, value_map))
                a_bfs = b_bfs
                b_bfs = []
            return answer_list

    def deduce_cells(self, board: 'AbstractBoard') -> bool:
        # 开玩笑 还真能写
        answer_list = self.bfs_get_states(board)
        pos_map = {}
        for line in answer_list:
            for pos in line:
                if pos not in pos_map:
                    pos_map[pos] = [line[pos], 1]
                else:
                    if pos_map[pos][0] == line[pos]:
                        pos_map[pos][1] += 1
        change = False
        for pos in pos_map:
            if pos_map[pos][1] == len(answer_list):
                if board.get_type(pos) == "N":
                    if pos_map[pos][0]:
                        board.set_value(pos, MINES_TAG)
                    else:
                        board.set_value(pos, VALUE_QUESS)
                    change = True
        return change

    def create_constraints(self, board: 'AbstractBoard', switch):
        model = board.get_model()
        s = switch.get(model, self)
        answer_list = self.bfs_get_states(board)
        var_list = []
        for index in range(len(answer_list)):
            line = answer_list[index]
            var = model.NewBoolVar(f"[3A]{self.pos}{index}")
            for pos, value in line.items():
                model.Add(board.get_variable(pos) == value).OnlyEnforceIf([var, s])
            var_list.append(var)
        if len(var_list) == 0:
            # 无解
            var = model.NewBoolVar(f"[3A]Error")
            model.Add(var == 1).OnlyEnforceIf(s)
            model.Add(var == 0).OnlyEnforceIf(s)
        model.Add(sum(var_list) == 1).OnlyEnforceIf(s)
