from dataclasses import dataclass
import time
import traceback

from flask import Response, jsonify, request

import minesweepervariants
from minesweepervariants.abs.board import AbstractBoard, AbstractPosition
from minesweepervariants.impl.rule.Rrule.Quess import RuleQuess
from minesweepervariants.impl.rule.Mrule.F import AbstractRule0F
from minesweepervariants.impl.summon.game import GameSession as Game, Mode, UMode, ValueAsterisk, MinesAsterisk
from minesweepervariants.impl.summon.summon import Summon
from minesweepervariants.impl.impl_obj import decode_board
from minesweepervariants.impl.summon.game import NORMAL, EXPERT, ULTIMATE, PUZZLE
from minesweepervariants.impl.summon.game import ULTIMATE_R, ULTIMATE_S, ULTIMATE_F, ULTIMATE_A, ULTIMATE_P
from minesweepervariants.utils.tool import get_random
from minesweepervariants.utils.impl_obj import get_seed, VALUE_QUESS, MINES_TAG
from minesweepervariants.utils.tool import hash_str

from .format import format_board, format_cell, format_gamemode
from ._typing import CellType, CellState, Board, ClickData, CountInfo, ComponentTemplate, ComponentConfig, CellConfig, \
    BoardMetadata, CreateGameParams, GenerateBoardResult, ResponseType, U_Hint, ClickResponse

__all__ = ["Model"]


@dataclass(slots=True)
class Model():
    game: Game | None
    rules: list[str]
    summon: Summon | None
    board: AbstractBoard | None
    noHint: bool
    noFail: bool

    def __init__(self, *args, **kwargs):
        self.game = None
        self.rules = []
        self.summon = None
        self.board = None
        self.noHint = True
        self.noFail = True

    def get_game(self):
        if self.game is None or self.game.board is None or self.game.answer_board is None:
            raise RuntimeError("游戏未初始化")
        return self.game

    def get_count(self) -> CountInfo:
        game = self.get_game()
        board = game.board
        a_board = game.answer_board

        count: CountInfo = {
            "total": len([_ for pos, _ in a_board("F")]),
            "known": None if game.drop_r else len([_ for pos, _ in a_board("F")]),
            "unknown": len([_ for _ in board("N")]),
            "remains": None if game.drop_r else len([_ for pos, _ in a_board("F") if board.get_type(pos) == "N"])
        }
        return count

    def generate_board(self) -> ResponseType[GenerateBoardResult]:
        data: GenerateBoardResult

        args: CreateGameParams = request.args  # type: ignore

        t = time.time()
        answer_board = None
        mask_board = None

        used_r = "true"
        rules = (args["rules"] or "V").split(",")
        total = int(args["total"] or -1)
        ultimate_mode = args.get("u_mode") or ""
        dye = args.get("dye") or ""
        mask = args.get("mask") or ""
        seed = args.get("seed") or None

        if seed is not None:
            get_random(new=True, seed=hash_str(seed))
        else:
            get_random(new=True)
            seed = str(get_seed())

        gamemode = args["mode"] or "EXPERT"
        print("rule: ", rules)

        mode: Mode | None = getattr(Mode, gamemode.upper(), None)
        if mode is None:
            raise ValueError(f"无效的游戏模式: {gamemode}")

        u_mode = UMode(0)
        if "+A" in ultimate_mode:
            u_mode |= ULTIMATE_A
        if "+F" in ultimate_mode:
            u_mode |= ULTIMATE_F
        if "+S" in ultimate_mode:
            u_mode |= ULTIMATE_S
        if "+R" in ultimate_mode:
            u_mode |= ULTIMATE_R
        if "+!" in ultimate_mode:
            u_mode |= ULTIMATE_P

        print(mode, u_mode)

        size_list = [int(i) for i in request.args.get("size", "5x5").split("x")]
        match size_list:
            case [width, height]:
                size = (width, height)
            case [length]:
                size = (length, length)
            case _:
                raise ValueError(f"无效的棋盘大小: {request.args.get('size')}")

        summon = Summon(
            size=size,
            total=total,
            rules=rules,
            drop_r=not used_r,
            mask=mask,
            dye=dye
        )

        self.summon = summon

        self.game = Game(
            summon=self.summon,
            mode=mode,
            drop_r=not used_r,
            ultimate_mode=u_mode
        )

        if isinstance(summon.mines_clue_rule, AbstractRule0F):
            self.game.flag_tag = MINES_TAG
        if isinstance(summon.clue_rule, RuleQuess):
            self.game.clue_tag = VALUE_QUESS

        if mode != PUZZLE:
            mask_board = None
            __t = time.time()
            __count = 0
            while __t + 9.5 > time.time():
                __count += 1
                answer_board = self.summon.summon_board()
                if answer_board is None:
                    get_random(new=True)
                    continue
                self.game.answer_board = answer_board
                mask_board = self.game.create_board()
                if mask_board is None:
                    get_random(new=True)
                    continue
                self.board = mask_board.clone()
                break
            if mask_board is None:
                raise ValueError(f"共尝试{__count}次, 均未生成成功")

        else:
            mask_board = self.summon.create_puzzle()
            answer_board = self.summon.answer_board
            self.game.answer_board = answer_board
            self.game.board = mask_board

        if dye:
            rules += [f"@{dye}"]
        if mask:
            rules += [f"&{mask}"]

        self.rules = rules[:]
        data = {
            "reason": '',
            "success": True
        }
        self.game.thread_hint()
        self.noFail = True
        self.noHint = True

        print(f"[new] 生成用时: {time.time() - t}s")
        print("[new]", data)
        return data, 200

    def metadata(self) -> ResponseType[BoardMetadata]:
        board_data: BoardMetadata
        print("[metadata] start")

        try:
            game = self.get_game()
        except RuntimeError as e:
            print("[metadata]", e)
            return {}, 200  # type: ignore

        board = game.board

        boards, cells, countint = format_board(board)

        mode, u_mode = format_gamemode(game.mode, game.ultimate_mode)

        board_data = {
            "seed": str(get_seed()),
            "mode": mode,
            "rules": self.rules,
            "count": self.get_count(),
            "noFail": self.noFail,
            "noHint": self.noHint,
            "u_mode": u_mode,
            "boards": boards,
            "cells": cells,
            "version": minesweepervariants.tuple_version()
        }

        if game.mode == ULTIMATE:
            deduced = game.deduced()
            board_data["u_hint"] = {
                "flagcount": len([
                    None for _pos in deduced if (
                        game.answer_board.get_type(_pos) == "F" and
                        _pos.board_key in game.answer_board.get_interactive_keys()
                    )]),
                "emptycount": len([
                    None for _pos in deduced if (
                        game.answer_board.get_type(_pos) == "C" and
                        _pos.board_key in game.answer_board.get_interactive_keys()
                    )])
            }
            if [key for key in board.get_board_keys() if key not in board.get_interactive_keys()]:
                board_data["u_hint"]["markcount"] = len([
                    None for _pos in deduced
                    if _pos.board_key not in game.board.get_interactive_keys()
                ])

        print("[metadata]", board_data)
        return board_data

    def click(self) -> ResponseType[ClickResponse]:
        refresh: ClickResponse

        cells: list[CellConfig] = []
        gameover = False
        win = False

        data: ClickData = request.get_json()

        print("[click] data:", data)

        game: Game = self.get_game()

        board = game.board.clone()
        pos = board.get_pos(data["x"], data["y"], data["boardName"])

        print("[click] start click")
        t = time.time()

        if data["button"] == "left":
            _board = game.click(pos)
        elif data["button"] == "right":
            _board = game.mark(pos)
        elif data["button"] == "Space":
            count = self.get_count()
            refresh = {
                "gameover": False,
                "success": True,
                "reason": "",
                "count": self.get_count(),
                "cells": cells,
                "noFail": self.noFail,
                "noHint": self.noHint,
            }
            if count["remains"] in (0, count["unknown"]):
                for pos, _ in self.game.board("N"):
                    self.game.board[pos] = self.game.answer_board[pos]
                refresh["gameover"] = True
                refresh["win"] = True
                refresh["count"] = self.get_count()
            return refresh
        else:
            _board = None
        print(f"[click] end click used time:{time.time() - t}s")
        game.thread_hint()
        game.thread_deduced()

        reason = ""
        if _board is None:
            unbelievable = None
            if data["button"] == "left":
                reason = "你踩雷了"
                unbelievable = game.unbelievable(pos, 0)
            elif data["button"] == "right":
                reason = "你标记了一个错误的雷"
                unbelievable = game.unbelievable(pos, 1)

            if unbelievable is None:
                raise RuntimeError
            self.noFail = False
            print("[click] *unbelievable*", unbelievable)
            mines: list[CellType] = [
                {"x": _pos.x, "y": _pos.y,
                 "boardname": _pos.board_key}
                for _pos in unbelievable
            ]
            gameover = True
            win = False
        else:
            for key in _board.get_board_keys():
                for pos, obj in _board(key=key):
                    if obj is None and board[pos] is None:
                        continue
                    if (
                        not (obj is None or board[pos] is None) and
                        obj.type() == board[pos].type() and
                        obj.code() == board[pos].code() and
                        obj.high_light(_board) == board[pos].high_light(board) and
                        obj.invalid(_board) == board[pos].invalid(board) and
                        obj.web_component == board[pos].web_component
                    ):
                        continue

                    label = obj not in [
                        VALUE_QUESS, MINES_TAG,
                        _board.get_config(key, "MINES"),
                        _board.get_config(key, "VALUE"),
                    ]
                    label = (
                            _board.get_config(key, "by_mini") and
                            label and
                            not (
                                    isinstance(obj, ValueAsterisk) or
                                    isinstance(obj, MinesAsterisk)
                            )
                    )
                    data = format_cell(_board, pos, label)
                    print("[click]", pos, obj, data)
                    cells.append(data)
            if not any(
                    _board.has("N", key=key) for
                    key in _board.get_interactive_keys()
            ):
                gameover = True
                reason = "你过关!!!(震声)"
                win = True

        print("[click] game.board:", game.board)

        _board = board if _board is None else _board
        refresh = {
            "gameover": gameover,
            "success": True,
            "reason": reason,
            "count": self.get_count(),
            "cells": cells,
            "noFail": self.noFail,
            "noHint": self.noHint,
        }

        if gameover:
            refresh["win"] = win
            if not win:
                refresh["mines"] = mines

        if game.mode == ULTIMATE:
            deduced = game.deduced()
            refresh["u_hint"] = {
                "flagcount": len([
                    None for _pos in deduced if (
                        game.answer_board.get_type(_pos) == "F" and
                        _pos.board_key in game.answer_board.get_interactive_keys()
                    )]),
                "emptycount": len([
                    None for _pos in deduced if (
                        game.answer_board.get_type(_pos) == "C" and
                        _pos.board_key in game.answer_board.get_interactive_keys()
                    )]),
            }
            if [key for key in board.get_board_keys() if key not in board.get_interactive_keys()]:
                refresh["u_hint"]["markcount"] = len([
                    None for _pos in deduced
                    if _pos.board_key not in game.board.get_interactive_keys()
                ])

        print("[click] refresh: " + str(refresh))
        return refresh, 200

    def hint_post(self):
        game = self.game
        print("[hint] hint start")
        t = time.time()
        hint_list = game.hint()
        print(hint_list)
        if [k for k in hint_list.values()][0]:
            self.noHint = False
        print(f"[hint] hint end: {time.time() - t}s")
        for hint in hint_list.items():
            print("[hint]", hint[0], "->", hint[1])
        # return {}, 200  # 格式和click返回应一样
        hint_list = hint_list.items()
        min_length = min(len(tup[0]) for tup in hint_list)
        print("[hint]", min_length)
        # 步骤2: 收集所有第一个列表长度等于最小长度的二元组
        hint_list = [tup for tup in hint_list if len(tup[0]) == min_length]

        if hint_list[0][1]:
            hint_list = [([], game.deduced())] + hint_list
        results = []

        # print(hint_list)
        for _b_hint, _t_hint in hint_list:
            print("[hint]", _b_hint, "->", _t_hint)
            b_hint = []
            t_hint = []
            for b in _b_hint:
                if type(b) is tuple:
                    if b[1] is None:
                        b_hint.append({
                            "rule": b[0],
                            "info": '',
                        })
                    else:
                        try:
                            for info in b_hint:
                                if "rule" not in info.keys():
                                    continue
                                if info["rule"] != b[0]:
                                    continue
                                info["info"] += ", " + b[1]
                                raise
                            b_hint.append({
                                "rule": b[0],
                                "info": "(" + b[1],
                            })
                        except Exception as e:
                            print("[hint] Error:", traceback.format_exc())
                elif isinstance(b, AbstractPosition):
                    b_hint.append({
                        "x": b.x,
                        "y": b.y,
                        "boardname": b.board_key,
                    })
            for b in b_hint:
                if "rule" not in b:
                    continue
                if b["info"] == "":
                    continue
                b["info"] += ")"
            for t in _t_hint:
                t_hint.append({
                    "x": t.x,
                    "y": t.y,
                    "boardname": t.board_key,
                })
            results.append({
                "condition": b_hint,
                "conclusion": t_hint
            })
        [print("[hint] hint:", _results) for _results in results]
        cells = []
        print(hint_list)
        for pos in hint_list[0][0]:
            if type(pos) is tuple:
                break
            obj = game.board[pos]
            label = obj not in [
                VALUE_QUESS, MINES_TAG,
                game.board.get_config(pos.board_key, "MINES"),
                game.board.get_config(pos.board_key, "VALUE"),
            ]
            label = (
                    game.board.get_config(pos.board_key, "by_mini") and
                    label and
                    not (
                            isinstance(obj, ValueAsterisk) or
                            isinstance(obj, MinesAsterisk)
                    )
            )
            cells.append(
                format_cell(game.board, pos, label)
            )
        data = {
            "hints": results,
            "noHint": self.noHint,
            "cells": cells
        }
        print("[hint] hint back: ", data)
        return jsonify(data), 200

    def get_rule_list(self):
        from minesweepervariants.impl.rule import get_all_rules
        from minesweepervariants.impl.board.dye import get_all_dye
        all_rules = get_all_rules()
        rules_info = {}
        for key in ["L", "M", "R"]:
            for name in all_rules[key]:
                unascii_name = [n for n in all_rules[key][name]["names"] if not n.isascii()]
                zh_name = unascii_name[0] if unascii_name else ""
                rules_info[name] = [
                    key.lower() + "Rule",
                    zh_name,
                    all_rules[key][name]["doc"]
                ]
        return {
            "rules": rules_info,
            "dye": get_all_dye()  # {dye_name: doc, minesweepervariants..}
        }

    def reset(self):

        game: Game = self.game
        mask_board = self.board.clone()
        print("[reset] reset start")
        print("[reset]", mask_board)
        if mask_board is None:
            print("[reset] board is None!")
            return {}, 500
        game.board = mask_board
        self.noFail = True
        self.noHint = True
        game.last_deduced = [None, []]
        game.last_hint = [None, {}]
        game.thread_deduced()
        game.thread_hint()
        if game.mode == ULTIMATE:
            if game.ultimate_mode & ULTIMATE_R:
                game.drop_r = False
            else:
                game.drop_r = True
        print("rest end")
        return '', 200
