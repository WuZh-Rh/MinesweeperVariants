#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/30 08:15
# @Author  : Wu_RH
# @FileName: app.py.py
import base64
import hashlib
import threading
import time
import traceback

from flask import jsonify, request, redirect
from flask_cors import CORS
import sys

from minesweepervariants.abs.board import AbstractPosition, AbstractBoard
from minesweepervariants.impl.summon.game import GameSession as Game, ValueAsterisk, MinesAsterisk
from minesweepervariants.impl.summon.summon import Summon
from minesweepervariants.impl.impl_obj import decode_board
from flask import Flask
import os
from minesweepervariants.impl.summon.game import NORMAL, EXPERT, ULTIMATE, PUZZLE
from minesweepervariants.impl.summon.game import ULTIMATE_R, ULTIMATE_S, ULTIMATE_F, ULTIMATE_A, ULTIMATE_P

from minesweepervariants.utils.impl_obj import get_seed, VALUE_QUESS, MINES_TAG
from minesweepervariants.utils.tool import get_logger

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入项目核心模块

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Referrer-Policy'] = 'unsafe-url'
    if 'Access-Control-Allow-Credentials' in response.headers:
        try:
            del response.headers['Access-Control-Allow-Credentials']
        except Exception:
            pass
    return response


hypothesis_data = dict()
github_web = "https://koolshow.github.io"


def format_cell(_board, pos, label):
    def init_component(data) -> dict:
        if data["type"] in ["col", "row"]:
            style = "display: flex; "
            if data["type"] == "col":
                # 垂直布局：主轴垂直方向，交叉轴居中
                style += "flex-direction: column;"
                # 子项高度平均分配（使用 flex-grow 实现）
                for child in data["children"]:
                    child_style = init_component(child).get("style", "")
                    if "flex-grow" not in child_style:
                        child_style += " flex-grow: 1;"
                    child["style"] = child_style
            else:
                # 水平布局：主轴水平方向，交叉轴居中
                style += "flex-direction: row;"
                # 子项宽度平均分配（使用 flex-grow 实现）
                for child in data["children"]:
                    child_style = init_component(child).get("style", "")
                    if "flex-grow" not in child_style:
                        child_style += " flex-grow: 1;"
                    child["style"] = child_style
            style += " align-items: center; justify-content: center; gap: 5%;"
            style += " width: 100%; height: 100%; flex-grow: 1;"
            return {
                "type": "container",
                "value": [init_component(i) for i in data["children"]],
                "style": style
            }

        elif data["type"] == "text":
            # 文本项：使用 flex 布局填充可用空间，添加溢出处理
            style = (f"color: rgb(from var({primary_color}) r g b / "
                     f"{50 if invalid else 100}%); text-align: center;")
            style += " display: flex; justify-content: center; align-items: center;"
            style += " flex: 1; min-width: 0; max-width: 100%;"  # 关键：允许内容收缩
            style += " overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"

            return {
                "type": "text",
                "value": data.get("text", ""),
                "style": style
            }

        elif data["type"] == "image":
            path = data.get("image")
            # 图片项：保持比例，居中显示
            return {
                "type": "assets",
                "value": path,
                "style": f"fill: rgb(from var({primary_color}) r g b / "
                         f"{50 if invalid else 100}%); flex: 1; min-width: 0;"
            }

        elif data["type"] == "placeholder":
            style = "flex-shrink: 0;"  # 防止占位符被压缩

            if "width" in data:
                # 行内容器中使用固定宽度
                style += f" width: {int(100 * data['width'])}%;"
            if "height" in data:
                # 列内容器中使用固定高度
                style += f" height: {int(100 * data['height'])}%;"

            return {
                "type": "container",
                "value": [],
                "style": style
            }

    obj = _board[pos]
    dye = _board.get_dyed(pos)
    primary_color = "--flag-color" if _board.get_type(pos) == "F" else "--foreground-color"
    invalid = False if obj is None else obj.invalid(_board)
    # print(obj.compose(_board, True))
    if hasattr(obj, "web_component"):
        cell_data = obj.web_component(_board)
    else:
        cell_data = init_component({
            "type": "row",
            "children": [obj.compose(_board, True)]
        })
        cell_data["style"] += " width: 100%; height: 100%; align-items: center; justify-content: center;"
    # if dye:
    #     cell_data["style"] += " background-color: rgb(from var(--foreground-color) r g b / 29%);"

    VALUE = _board.get_config(pos.board_key, "VALUE")
    MINES = _board.get_config(pos.board_key, "MINES")
    if obj in [VALUE, MINES, None]:
        overlayText = ""
    else:
        overlayText = obj.type().decode("ascii")
    # hightlight = [{
    #             "x": pos.x,
    #             "y": pos.y,
    #             "boardname": pos.board_key,
    #         }]
    hightlight = {pos.board_key: [[pos.x, pos.y]]}
    if obj is not None:
        if obj.high_light(_board) is not None:
            for h_pos in set(h_pos for h_pos in obj.high_light(_board) if _board.in_bounds(h_pos)):
                # hightlight.append({
                #     "x": h_pos.x,
                #     "y": h_pos.y,
                #     "boardname": h_pos.board_key,
                # })
                if h_pos.board_key not in hightlight:
                    hightlight[h_pos.board_key] = []
                hightlight[h_pos.board_key].append([h_pos.x, h_pos.y])
    cell_data = {
        "type": "" if obj is None else obj.type().decode("ascii"),
        "position": {
            "x": pos.x, "y": pos.y,
            "boardname": pos.board_key
        },
        "component": cell_data,
        "highlight": hightlight,
        "clickable": True,
        "overlayText": overlayText if label else ""
    }
    # import json
    # json_str = json.dumps(cell_data, separators=(",", ":"))
    # print(json_str)
    return cell_data


def format_board(_board: AbstractBoard):
    if _board is None:
        return
    # board: Board
    board_data: dict = {
        "boards": {},
        "cells": [],
    }
    count = 0
    for key in _board.get_board_keys():
        dye_list = [
            [_board.get_dyed(pos) if _board.is_valid(pos) else False
             for pos in _board.get_row_pos(col_pos)]
            for col_pos in _board.get_col_pos(
                _board.boundary(key=key)
            )
        ]
        mask_list = [
            [not _board.is_valid(pos) for pos in _board.get_row_pos(col_pos)]
            for col_pos in _board.get_col_pos(
                _board.boundary(key=key)
            )
        ]
        board_data["boards"][key] = {
            "size": _board.get_config(key, "size"),
            "position": [_board.get_board_keys().index(key), 0],
            "showLabel": _board.get_config(key, "row_col"),
            "showName": not _board.get_config(key, "row_col"),  # TODO 何时不显示Name?
            # TODO X=N, poslabel
        }
        print(mask_list)
        if any(any(i) for i in mask_list):
            board_data["boards"][key].update({
                "mask": mask_list
            })
        if any(any(i) for i in dye_list):
            board_data["boards"][key].update({
                "dye": dye_list,
            })
        for pos, obj in _board(key=key):
            if obj is None:
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
            board_data["cells"].append(
                format_cell(_board, pos, label))
            count += 1
    board_data["count"] = count
    import json
    json_str = json.dumps(board_data, separators=(",", ":"))
    print(json_str)
    return board_data


def hash_str(s):
    try:
        return int(s)
    except ValueError:
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return int(h[:4], 16)


@app.route('/')
def root():
    return redirect("https://koolshow.github.io/MinesweeperVariants-Vue/")


@app.route('/api/new')
def generate_board():
    global hypothesis_data
    from minesweepervariants.utils.tool import get_random
    from minesweepervariants.impl.rule.Rrule.Quess import RuleQuess
    from minesweepervariants.abs.Mrule import Rule0F
    get_random(new=True)
    # get_random(new=True, seed=1145141919810)
    # get_random(new=True, seed=4096695)
    t = time.time()
    answer_board = None
    mask_board = None
    code = request.args.get("code", None)
    # code = ""
    used_r = request.args.get("used_r", "true").lower() == "true"
    rules = request.args.get("rules", "V")
    ultimate_mode = request.args.get("u_mode", "+A")
    total = int(request.args.get("total", -1))
    dye = request.args.get("dye", "")
    mask = request.args.get("mask", "")
    seed = request.args.get("seed", None)
    if rules:
        rules = rules.split(",")
    else:
        rules = ["V"]
    if seed is not None:
        get_random(new=True, seed=hash_str(seed))
    # dye = "@c"
    gamemode = request.args.get("mode", "EXPERT")
    print("rule: ", rules)
    mode = 1
    match gamemode:
        case "NORMAL":
            mode = NORMAL
        case "EXPERT":
            mode = EXPERT
        case "ULTIMATE":
            mode = ULTIMATE
        case "PAZZLE":
            mode = PUZZLE
    u_mode = 0
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

    print(mode)
    # print(123456)
    if code:
        code, mask_code, *rules = code.split(":")
        rules = [base64.urlsafe_b64decode(rule_code.encode("utf-8")).decode("utf-8") for rule_code in rules]
        print(code, mask_code, rules)
        answer_board = decode_board(code, None)
        mask_code = int.from_bytes(bytes.fromhex(mask), "big", signed=False)
        mask_board = answer_board.clone()
        for key in answer_board.get_board_keys():
            for pos, _ in answer_board(key=key):
                if mask_code & 1:
                    mask_board[pos] = None
                mask_code >>= 1
        master_key = mask_board.get_board_keys()[0]
        size = mask_board.get_config(master_key, "size")
    else:
        size = [int(i) for i in request.args.get("size", None).split("x")]
    try:
        summon = Summon(
            size=size,
            total=total,
            rules=rules,
            drop_r=not used_r,
            mask=mask,
            dye=dye
        )
        hypothesis_data["summon"] = summon
    except Exception as e:
        return {
            "reason": traceback.format_exc(),
            "success": False
        }
    game = Game(
        summon=hypothesis_data["summon"],
        mode=mode,
        drop_r=not used_r,
        ultimate_mode=u_mode
    )

    hypothesis_data["game"] = game
    if isinstance(summon.clue_rule, RuleQuess):
        game.clue_tag = VALUE_QUESS
    if isinstance(summon.mines_clue_rule, Rule0F):
        game.flag_tag = MINES_TAG
    if code:
        hypothesis_data["game"].answer_board = answer_board
        hypothesis_data["game"].board = mask_board
    else:
        # print(2)
        if mode < PUZZLE:
            try:
                mask_board = None
                __t = time.time()
                __count = 0
                while __t + 9.5 > time.time():
                    __count += 1
                    answer_board = hypothesis_data["summon"].summon_board()
                    if answer_board is None:
                        get_random(new=True)
                        continue
                    hypothesis_data["game"].answer_board = answer_board
                    mask_board = hypothesis_data["game"].create_board()
                    if mask_board is None:
                        get_random(new=True)
                        continue
                    hypothesis_data["board"] = mask_board.clone()
                    break
                if mask_board is None:
                    raise ValueError(f"共尝试{__count}次, 均未生成成功")
            except Exception as e:
                return {
                    "reason": traceback.format_exc(),
                    "success": False
                }
        else:
            try:
                mask_board = hypothesis_data["summon"].create_puzzle()
                answer_board = hypothesis_data["summon"].answer_board
                hypothesis_data["game"].answer_board = answer_board
                hypothesis_data["game"].board = mask_board
            except Exception as e:
                return {
                    "reason": traceback.format_exc(),
                    "success": False
                }
    if dye:
        rules += [f"@{dye}"]
    if mask:
        rules += [f"&{mask}"]
        # answer_board = hypothesis_data["game"].answer_board
    # print(hypothesis_data)
    # print(answer_board.show_board())
    # hypothesis_data["game"].deduced(wait=False)
    hypothesis_data["rules"] = rules[:]
    data = {
        "reason": '',
        "success": True
    }
    hypothesis_data["game"].thread_hint()
    hypothesis_data["data"] = {}
    hypothesis_data["data"]["noFail"] = True
    hypothesis_data["data"]["noHint"] = True
    # hypothesis_data["game"].thread_deduced()
    print(f"生成用时: {time.time() - t}s")
    print(data)
    return jsonify(data), 200


@app.route('/api/metadata')
def metadata():
    print('metadata')
    if "game" not in hypothesis_data \
            or hypothesis_data["game"].board is None \
            or hypothesis_data["game"].answer_board is None:
        print("fail")
        return {}, 200
    game = hypothesis_data["game"]
    if game.board is None:
        return {}, 200
    if game.answer_board is None:
        return {}, 200
    board = game.board
    a_board = game.answer_board

    board_data = format_board(board)
    count = dict()
    count["total"] = len([_ for pos, _ in a_board("F")])
    count["unknown"] = len([_ for _ in board("N")])
    if hypothesis_data["game"].drop_r:
        count["known"] = None
        count["remains"] = None
    else:
        count["known"] = len([_ for pos, _ in a_board("F")])
        count["remains"] = len([_ for pos, _ in a_board("F") if board.get_type(pos) == "N"])
    board_data["rules"] = hypothesis_data["rules"]
    board_data["count"] = count
    board_data["noFail"] = hypothesis_data["data"]["noFail"]
    board_data["noHint"] = hypothesis_data["data"]["noHint"]
    board_data["u_mode"] = []
    gamemode = game.mode
    u_gamemode = game.ultimate_mode
    if gamemode == NORMAL:
        board_data["mode"] = "NORMAL"
    elif gamemode == EXPERT:
        board_data["mode"] = "EXPERT"
    elif gamemode == ULTIMATE:
        board_data["mode"] = "ULTIMATE"
        board_data["u_mode"] = []
        if u_gamemode & ULTIMATE_A:
            board_data["u_mode"].append("+A")
        if u_gamemode & ULTIMATE_F:
            board_data["u_mode"].append("+F")
        if u_gamemode & ULTIMATE_S:
            board_data["u_mode"].append("+S")
        if u_gamemode & ULTIMATE_R:
            board_data["u_mode"].append("+R")
        if u_gamemode & ULTIMATE_P:
            board_data["u_mode"].append("+!")
    elif gamemode == PUZZLE:
        board_data["mode"] = "PUZZLE"
    else:
        board_data["mode"] = "UNKNOWN"
    board_data["seed"] = str(get_seed())
    print(board_data)
    return jsonify(board_data)


@app.route('/api/click', methods=['POST', 'GET'])
def click():
    global hypothesis_data
    data = request.get_json()
    refresh = {
        "cells": [],
        "gameover": False,
        "success": True,
        "reason": "",
        "count": {}
    }
    print(data)
    # print(hypothesis_data)
    game: Game = hypothesis_data["game"]
    summon = hypothesis_data["summon"]
    if game.mode == ULTIMATE:
        deduced = game.deduced()
        refresh["u_hint"] = {
            "flagcount": len([None for _pos in deduced if game.answer_board.get_type(_pos) == "F"]),
            "emptycount": len([None for _pos in deduced if game.answer_board.get_type(_pos) == "C"]),
            "markcount": len([None for _pos in deduced if _pos.board_key not in game.board.get_interactive_keys()])
        }
    # print(game.board.show_board())
    board = game.board.clone()
    pos = board.get_pos(data["x"], data["y"], data["boardName"])
    # if data["x"] == 0 and data["y"] == 0:
    #     print(hypothesis_data["game"].hint(wait=True))
    #     print(hypothesis_data["game"].deduced(wait=True))
    #     return {}
    print("start click")
    t = time.time()
    if data["button"] == "left":
        _board = game.click(pos)
    elif data["button"] == "right":
        _board = game.mark(pos)
    else:
        _board = None
    print(f"end click used time:{time.time() - t}s")
    hypothesis_data["game"].thread_hint()
    hypothesis_data["game"].thread_deduced()

    if _board is None:
        unbelievable = None
        if data["button"] == "left":
            refresh["reason"] = "你踩雷了"
            unbelievable = game.unbelievable(pos, 0)
        elif data["button"] == "right":
            refresh["reason"] = "你标记了一个错误的雷"
            unbelievable = game.unbelievable(pos, 1)
        if unbelievable is None:
            return {}, 500
        hypothesis_data["data"]["noFail"] = False
        print("*unbelievable*", unbelievable)
        refresh["mines"] = [
            {"x": _pos.x, "y": _pos.y,
             "boardname": _pos.board_key}
            for _pos in unbelievable
        ]
        refresh["gameover"] = True
        refresh["win"] = False
    else:
        if game.mode == ULTIMATE:
            if pos.board_key in board.get_interactive_keys():
                if data["button"] == "left":
                    refresh["u_hint"]["flagcount"] -= 1
                elif data["button"] == "right":
                    refresh["u_hint"]["emptycount"] -= 1
            else:
                refresh["u_hint"]["markcount"] -= 1
        for key in _board.get_board_keys():
            for pos, obj in _board(key=key):
                if obj is None and board[pos] is None:
                    continue
                if (
                    not (obj is None or board[pos] is None) and
                    obj.type() == board[pos].type() and
                    obj.code() == board[pos].code() and
                    obj.high_light(_board) == board[pos].high_light(board) and
                    obj.invalid(_board) == board[pos].invalid(board)
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
                print(pos, obj, data)
                refresh["cells"].append(data)
        if not any(
            _board.has("N", key=key) for
            key in _board.get_interactive_keys()
        ):
            refresh["gameover"] = True
            refresh["reason"] = "你过关!!!(震声)"
            refresh["win"] = True
    print(game.board)
    # print(game.deduced())
    # print(game.hint())
    # print(refresh)
    # if _board:
    #     print(_board.show_board())
    #     print(game.deduced())
    #     print(game.last_hint[1])
    # hypothesis_data["game"].deduced(wait=False)
    a_board = hypothesis_data["game"].answer_board
    _board = board if _board is None else _board
    count = dict()
    count["total"] = len([_ for pos, _ in a_board("F")])
    count["unknown"] = len([_ for _ in _board("N")])
    if hypothesis_data["game"].drop_r:
        count["known"] = None
        count["remains"] = None
    else:
        count["known"] = len([_ for pos, _ in a_board("F")])
        count["remains"] = len([_ for pos, _ in a_board("F") if _board.get_type(pos) == "N"])
    refresh["count"] = count
    refresh["noFail"] = hypothesis_data["data"]["noFail"]
    refresh["noHint"] = hypothesis_data["data"]["noHint"]
    print("refresh: " + str(refresh))
    return refresh, 200


@app.route('/api/hint', methods=['POST', 'GET'])
def hint_post():
    global hypothesis_data
    game = hypothesis_data["game"]
    print("hint start")
    t = time.time()
    hint_list = game.hint()
    if [k for k in hint_list.keys()][0]:
        hypothesis_data["data"]["noHint"] = False
    print(f"hint end: {time.time() - t}s")
    for hint in hint_list.items():
        print(hint[0], "->", hint[1])
    # return {}, 200  # 格式和click返回应一样
    hint_list = hint_list.items()
    min_length = min(len(tup[0]) for tup in hint_list)
    print(min_length)
    # 步骤2: 收集所有第一个列表长度等于最小长度的二元组
    hint_list = [tup for tup in hint_list if len(tup[0]) == min_length]

    if hint_list[0][1]:
        hint_list = [([], game.deduced())] + hint_list
    results = []

    # print(hint_list)
    for _b_hint, _t_hint in hint_list:
        print(_b_hint, "->", _t_hint)
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
                        print(e)
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
    [print("hint:", _results) for _results in results]
    cells = []
    print(hint_list)
    for pos in hint_list[0][0]:
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
        "noHint": hypothesis_data["data"]["noHint"],
        "cells": cells
    }
    print("hint back: ", data)
    return jsonify(data), 200


@app.route('/api/rules', methods=['POST', 'GET'])
def get_rule_list():
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


@app.route('/api/reset', methods=['POST', 'GET'])
def reset():
    global hypothesis_data
    game: Game = hypothesis_data["game"]
    mask_board = hypothesis_data["board"].clone()
    print("reset start")
    print(mask_board)
    if mask_board is None:
        print("board is None")
        return {}, 500
    game.board = mask_board
    hypothesis_data["data"]["noFail"] = True
    hypothesis_data["data"]["noHint"] = True
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


if __name__ == '__main__':
    get_logger(log_lv="DEBUG")
    port = int(sys.argv[1] if len(sys.argv) == 2 else "5050")
    # 允许所有来源跨域，或根据需要设置 origins=["*"]

    # threading.Thread(target=lambda: webbrowser.open(f"http://localhost:{port}", new=2)).start()
    import waitress

    print(f"server start at 0.0.0.0:{port}")
    waitress.serve(app, host='0.0.0.0', port=port)
