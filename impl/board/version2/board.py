#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import gc
# @Time    : 2025/06/03 01:58
# @Author  : Wu_RH
# @FileName: board.py

from typing import List, Union, Tuple, Any, Generator, TYPE_CHECKING
import heapq

from ortools.sat.python.cp_model import IntVar

from abs.rule import AbstractValue
from utils.impl_obj import VALUE_QUESS, MINES_TAG
from utils.impl_obj import POSITION_TAG, VALUE_CROSS, VALUE_CIRCLE
from utils.tool import get_logger
from .dye import get_dye
from utils.solver import get_model
from abs.board import AbstractBoard, AbstractPosition, MASTER_BOARD
from abs.Rrule import AbstractClueValue
from abs.Mrule import AbstractMinesValue

if TYPE_CHECKING:
    ...


def get_value(pos=None, code=None):
    from impl.impl_obj import get_value
    return get_value(pos, code)


class Position(AbstractPosition):
    def __repr__(self):
        if self.y > 25:
            return ""
        return (f"{'['+self.board_key+']' if self.board_key != MASTER_BOARD else ''}"
                f"{'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[self.y]}{self.x+1}")

    def _up(self, n: int = 1):
        self.x -= n

    def _down(self, n: int = 1):
        self.x += n

    def _left(self, n: int = 1):
        self.y -= n

    def _right(self, n: int = 1):
        self.y += n

    def _deviation(self, pos: 'Position'):
        self.x += pos.x
        self.y += pos.y

    def in_bounds(self, bound_pos: 'Position') -> bool:
        if bound_pos.board_key != self.board_key:
            return False
        return (0 <= self.x <= bound_pos.x and
                0 <= self.y <= bound_pos.y)

    def neighbors(self, *args: int) -> list['Position']:
        """
        按照欧几里得距离从小到大逐层扩散，筛选范围由距离平方控制（不包含当前位置）。

        调用方式（类似 range）：
            neighbors(end_layer)
                返回所有欧几里得距离 ≤ √end_layer 的位置（从第 1 层开始）。
            neighbors(start_layer, end_layer)
                返回所有欧几里得距离 ∈ [√start_layer, √end_layer] 的位置。

        :param args: 一个或两个整数
            - 若提供一个参数 end_layer，视为从 √1 到 √end_layer。
            - 若提供两个参数 start_layer 和 end_layer，视为从 √start_layer 到 √end_layer。
            - 参数非法（数量不为 1 或 2，或值非法）时返回空列表。

        :return: 位置列表，按距离从近到远排序。
        """

        # 解析参数
        if len(args) == 1:
            low, high = 1, args[0]
        elif len(args) == 2:
            low, high = args
        else:
            return []

        # 处理无效参数
        if high < low:
            return []

        x0, y0 = self.x, self.y
        directions = [(dx, dy) for dx in (-1, 0, 1)
                      for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]

        heap = []  # 最小堆存储 (距离平方, x, y)
        visited = {(x0, y0)}
        result = []

        # 处理包含自身的情况 (距离平方=0)
        if low <= 0 <= high:
            result.append(self.clone())

        # 初始化邻居
        for dx, dy in directions:
            nx, ny = x0 + dx, y0 + dy
            d_sq = (nx - x0) ** 2 + (ny - y0) ** 2
            if d_sq <= high:
                heapq.heappush(heap, (d_sq, nx, ny))
                visited.add((nx, ny))

        # 遍历所有可达位置
        while heap:
            d_sq, x, y = heapq.heappop(heap)

            # 检查是否在目标范围内
            if low <= d_sq <= high:
                result.append(Position(x, y, self.board_key))

            # 扩展新位置
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited:
                    continue

                visited.add((nx, ny))
                new_d_sq = (nx - x0) ** 2 + (ny - y0) ** 2

                # 仅考虑距离平方未超过上限的位置
                if new_d_sq <= high:
                    heapq.heappush(heap, (new_d_sq, nx, ny))

        return result


class Board(AbstractBoard):
    """
    通过实现
    """
    name = "Board1"
    version = 1
    board_data: dict

    def __init__(self, size: tuple = None, code: bytes = None):
        self.model_id = None
        self.board_data = dict()

        if code is None:
            if size is None:
                raise ValueError("board size Undefined")
            self.generate_board(MASTER_BOARD, size=size)
            self.board_data[MASTER_BOARD]["config"]["row_col"] = True
            self.board_data[MASTER_BOARD]["config"]["interactive"] = True
            self.board_data[MASTER_BOARD]["config"]["VALUE"] = VALUE_QUESS
            self.board_data[MASTER_BOARD]["config"]["MINES"] = MINES_TAG
            return
        for chunks in code.split(b"\xff\xff"):
            board_key, chunks = chunks.split(b"\xff", 1)
            board_key = board_key.decode("ascii")
            self.generate_board(board_key, code=chunks)

    def __call__(
            self, target: Union[str, None] = "always",
            mode: str = "object",
            key: str = None,
    ) -> Generator[
        Tuple[
            'Position',
            Union[
            'AbstractClueValue',
            'AbstractMinesValue',
            str, IntVar, bool, None
            ]],
        Any, None
    ]:
        """
        被调用时循环返回目标值

        @:param
            target (str): 遍历目标类型。可选值：
                - "C": 线索 (Clue)
                - "F": 雷 (Mines)
                - "N": 未定义或未翻开
                - "always": 默认，遍历所有

            mode (str): 返回的目标类型, 可选值:
                - "object":     存储在board内的实例对象
                - "type":       对象的类型('C', 'F', 'N')
                - "variable":   变量对象
                - "dye":        染色bool

        @:return
            当前位置与选择的值。
        """
        if key is None:
            for key in self.get_interactive_keys():
                for i in self(target=target, mode=mode, key=key):
                    yield i
        else:
            size = self.board_data[key]["config"]["size"]
            for posx in range(size[0]):
                for posy in range(size[1]):
                    pos = Position(posx, posy, key)
                    pos_type = self.get_type(pos)

                    # 检查是否符合目标类型
                    if target == "always" or pos_type in target:
                        if mode == "object":
                            yield pos, self.get_value(pos)
                        elif mode == "type":
                            yield pos, pos_type
                        elif mode == "variable":
                            yield pos, self.get_variable(pos)
                        elif mode == "dye":
                            yield pos, self.get_dyed(pos)
                        elif mode == "none":
                            yield pos, None

    def has(self, target: str, key: str = None) -> bool:
        for board_key in self.board_data:
            if board_key != key and key is not None:
                continue
            for line in self.board_data[board_key]["type"]:
                for type_obj in line:
                    if type_obj == target:
                        return True
        return False

    def generate_board(
            self, board_key: str,
            size: tuple = (),
            code: bytes = None,
            true_tag: "AbstractValue" = VALUE_CROSS,
            false_tag: "AbstractValue" = VALUE_CIRCLE,
    ) -> None:
        """
        创建一个新的题板
        :param board_key: 题板名称
        :param size: 题板的尺寸 (与code二选一)
        :param code: 题板的代码 (与size二选一)
        :param true_tag: 题板默认非雷对象
        :param false_tag:题板默认雷对象
        """
        if board_key in self.board_data:
            return
        flag_byte = 0
        if code is not None:
            config, ture_code, false_code, code\
                = code.split(b"\xff", 3)
            *size, flag_byte = config
            size = (size[0], size[1])
            true_tag = get_value(pos=POSITION_TAG, code=ture_code)
            false_tag = get_value(pos=POSITION_TAG, code=false_code)
        data = dict()
        self.board_data[board_key] = data
        # 配置初始化
        data["config"] = {
            "size": size,
            "VALUE": true_tag,
            "MINES": false_tag
        }
        for key in self.CONFIG_FLAGS:
            data["config"].update({key: False})

        data["obj"] = [[None for _ in range(size[0])] for _ in range(size[1])]
        data["type"] = [["N" for _ in range(size[0])] for _ in range(size[1])]
        data["dye"] = [[False for _ in range(size[0])] for _ in range(size[1])]
        if code is None:
            return

        for i, key in enumerate(self.CONFIG_FLAGS[::-1]):
            data["config"].update({key: bool(flag_byte & (1 << i))})

        codes = code.split(b"\xff")

        code_queue = []

        for part in codes:
            if not part:
                continue
            if part[0] == 0:
                count = int(part[1])
                code_queue.extend([b'_'] * count)
            else:
                code_queue.append(part)

        for pos, _ in self(key=board_key):
            code = code_queue.pop(0)
            if code[0] == 35:
                self.set_dyed(pos, True)
                code = code[1:]
            if code == b'_':
                continue
            value = get_value(pos, code)
            if value is not None:
                self.set_value(pos, value)
                continue
            raise ValueError(f"unknown type{code}")

    def boundary(self, key=MASTER_BOARD) -> "Position":
        if key not in self.get_board_keys():
            return Position(-1, -1, key)
        size = self.board_data[key]["config"]["size"]
        return Position(size[0] - 1, size[1] - 1, key)

    def encode(self) -> bytes:
        """
        字节头: 尺寸
        无需换行符 初始化自动排序
        '_'表示None
        :return: 字节码
        """
        board_bytes = bytearray()
        for board_key in self.board_data:
            size = self.board_data[board_key]["config"]["size"]
            value = self.board_data[board_key]["config"]["VALUE"]
            mines = self.board_data[board_key]["config"]["MINES"]
            flags = 0
            for name in self.CONFIG_FLAGS:
                flags = (flags << 1) | int(self.board_data[board_key]["config"].get(name, False))
            board_bytes.extend(board_key.encode("ascii") + b"\xff")
            board_bytes.extend(bytes([size[0], size[1], flags, 255]))
            board_bytes.extend(value.type() + b"|" + value.code())
            board_bytes.extend(bytes([255]))
            board_bytes.extend(mines.type() + b"|" + mines.code())
            # key | sizex | sizey | config
            for pos, obj in self(key=board_key):
                board_bytes.extend(b"\xff")
                if self.get_dyed(pos):
                    board_bytes.extend(b"#")
                if obj is None:
                    board_bytes.extend(b"_")
                else:
                    code = obj.code()
                    if b"\xff" in code:
                        get_logger().error(f"{obj.type().decode()}中编码出现\\xff")
                        raise ValueError(r"code contains forbidden byte: \xff")
                    board_bytes.extend(obj.type() + b"|" + code)
            board_bytes.extend(b"\xff\xff")
        # 只用split(b"\xff_")切分
        parts = board_bytes.split(b"\xff_")

        # 处理连续 \xff_ 的次数
        encoded_bytes = bytearray()
        i = 0
        while i < len(parts):
            if i > 0:
                # 统计连续 \xff_ 的次数
                count = 1
                # 看后续parts里是否以空字节开头来判断是否连续（split后的空串）
                # 但这里由于只分割 \xff_，连续情况只能靠检查下一个part是否空
                while i + count < len(parts) and parts[i + count - 1] == b'':
                    count += 1
                # 输出 \xff + 数字（表示连续多少个 \xff_）
                while count > 254:
                    encoded_bytes.extend(b"\xff\x00" + bytes([254]))
                    count -= 254
                if count > 0:
                    encoded_bytes.extend(b"\xff\x00" + bytes([count]))
                i += count - 1
            encoded_bytes.extend(parts[i])
            i += 1

        return encoded_bytes[:-2]

    @staticmethod
    def type_value(value) -> str:
        # 查看value的类型
        if value is None:
            return "N"
        elif isinstance(value, AbstractMinesValue):
            return "F"
        elif isinstance(value, AbstractClueValue):
            return "C"
        get_logger().error(f"unknown type: value{value}, type{type(value)}")
        raise ValueError(f"unknown type: {value}, type{type(value)}")

    def get_type(self, pos: 'Position') -> str:
        key = pos.board_key
        size = self.board_data[key]["config"]["size"]
        if 0 <= pos.x < size[0] and 0 <= pos.y < size[1]:
            return self.board_data[key]["type"][pos.y][pos.x]
        return ""

    def get_value(self, pos: 'Position') -> Union['AbstractClueValue', 'AbstractMinesValue', None]:
        key = pos.board_key
        size = self.board_data[key]["config"]["size"]
        if 0 <= pos.x < size[0] and 0 <= pos.y < size[1]:
            return self.board_data[key]["obj"][pos.y][pos.x]
        return None

    def set_value(self, pos: 'Position', value):
        key = pos.board_key
        size = self.board_data[key]["config"]["size"]
        if 0 <= pos.x < size[0] and 0 <= pos.y < size[1]:
            self.board_data[key]["obj"][pos.y][pos.x] = value
            self.board_data[key]["type"][pos.y][pos.x] = self.type_value(value)

    def dyed(self, name: str):
        get_dye(name)().dye(self)

    def get_dyed(self, pos: 'Position') -> bool | None:
        key = pos.board_key
        size = self.board_data[key]["config"]["size"]
        if 0 <= pos.x < size[0] and 0 <= pos.y < size[1]:
            return self.board_data[key]["dye"][pos.y][pos.x]

    def set_dyed(self, pos: 'Position', dyed: bool):
        key = pos.board_key
        size = self.board_data[key]["config"]["size"]
        if 0 <= pos.x < size[0] and 0 <= pos.y < size[1]:
            self.board_data[key]["dye"][pos.y][pos.x] = dyed

    def get_variable(self, pos: 'Position') -> IntVar | None:
        key = pos.board_key
        model = get_model()
        size = self.board_data[key]["config"]["size"]
        if id(model) != self.model_id:
            self.model_id = id(model)
            for _key in self.board_data:
                _size = self.board_data[_key]["config"]["size"]
                if "variable" in self.board_data[_key]:
                    del self.board_data[_key]["variable"]
                self.board_data[_key]["variable"] = \
                    [[model.NewBoolVar(f"{_key}.{x}.{y}")
                      for y in range(_size[0])]
                     for x in range(_size[1])]
                get_logger().trace(f"构建新变量:{self.board_data[_key]['variable']}")
        if 0 <= pos.x < size[0] and 0 <= pos.y < size[1]:
            return self.board_data[key]["variable"][pos.y][pos.x]

    def clear_variable(self):
        for key in self.board_data.keys():
            if "variable" in self.board_data[key]:
                del self.board_data[key]["variable"]
        gc.collect()
        self.model_id = None

    def get_config(self, board_key, config_name):
        if board_key not in self.board_data:
            return None
        return self.board_data[board_key]["config"][config_name]

    def set_config(self, board_key, config_name, value: bool):
        if board_key not in self.board_data:
            return None
        self.board_data[board_key]["config"][config_name] = value

    def get_row_pos(self, pos: 'Position') -> List["Position"]:
        _pos = pos.clone()
        pos_list = [_pos]
        while True:
            _pos = _pos.left()
            if not self.in_bounds(_pos):
                break
            pos_list.append(_pos)
        _pos = pos.clone()
        pos_list = pos_list[::-1]
        while True:
            _pos = _pos.right()
            if not self.in_bounds(_pos):
                break
            pos_list.append(_pos)
        return pos_list

    def get_col_pos(self, pos: 'Position') -> List["Position"]:
        _pos = pos.clone()
        pos_list = [_pos]
        while True:
            _pos = _pos.up()
            if not self.in_bounds(_pos):
                break
            pos_list.append(_pos)
        _pos = pos.clone()
        pos_list = pos_list[::-1]
        while True:
            _pos = _pos.down()
            if not self.in_bounds(_pos):
                break
            pos_list.append(_pos)
        return pos_list

    def get_pos(self, x: int, y: int, key=MASTER_BOARD) -> Union['Position', None]:
        size = self.board_data[key]["config"]["size"]
        if -size[0] < x < size[0] and -size[1] < y < size[1]:
            x = x if x >= 0 else size[0] + x
            y = y if y >= 0 else size[1] + y
            return Position(x, y, key)
        return None

    def batch(self, positions: List['Position'],
              mode: str, drop_none: bool = False) -> List[Any]:
        result = []
        for pos in positions:
            if drop_none and not self.in_bounds(pos):
                continue
            if mode == "object":
                result.append(self.get_value(pos))
            elif mode == "variable":
                result.append(self.get_variable(pos))
            elif mode == "type":
                result.append(self.get_type(pos))
            elif mode == "dye":
                result.append(self.get_dyed(pos))
            else:
                raise ValueError(f"Unsupported mode: {mode}")
        return result

    def clear_board(self):
        for key in self.board_data:
            data = self.board_data[key]
            size = data["config"]["size"]
            data["obj"] = [[None for _ in range(size[0])] for _ in range(size[1])]
            data["type"] = [["N" for _ in range(size[0])] for _ in range(size[1])]
            self.clear_variable()
            self.model_id = None

    def get_board_keys(self) -> list[str]:
        return list(self.board_data.keys())

    def show_board(self, show_tag: bool = False):
        r = ""
        for key in self.board_data:
            size = self.board_data[key]["config"]["size"]
            if len(self.board_data.keys()) > 1:
                r += key + "\n"
            for i in range(size[0]):
                for j in range(size[1]):
                    value = self[self.get_pos(i, j, key)]
                    if value is None:
                        r += "______" if show_tag else "___"
                    else:
                        r += str(value) + ("_" + value.type().decode() if show_tag else "")
                    r += "\t"
                r += "\n"
            r += "\n\n"
        return r[:-2]
