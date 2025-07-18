#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/06/15 11:59
# @Author  : Wu_RH
# @FileName: 1T'.py

"""
[1T']必三连: 雷必然处在横竖对角构成三连
"""

from abs.Lrule import AbstractMinesRule
from abs.board import AbstractBoard
from utils.solver import get_model
from utils.tool import get_logger


class Rule1Tp(AbstractMinesRule):
    name = "1T'"
    subrules = [
        [True, "[1T']雷必三连"]
    ]

    def create_constraints(self, board: 'AbstractBoard'):
        if not self.subrules[0][0]:
            return

        model = get_model()
        logger = get_logger()

        # 存储每个位置所属的三连组变量
        position_coverage = {pos: [] for pos, _ in board()}

        # 生成所有可能的三连组（8个方向）
        for pos, _ in board():
            # 定义8个方向：右/左/下/上/右下/左下/右上/左上
            directions = [
                (0, 1), (0, -1), (1, 0), (-1, 0),  # 横竖
                (1, 1), (1, -1), (-1, 1), (-1, -1)  # 对角线
            ]

            for dx, dy in directions:
                positions = [
                    pos,
                    pos.shift(dx, dy),
                    pos.shift(2 * dx, 2 * dy)
                ]

                # 检查所有位置是否在棋盘内
                if all(board.is_valid(p) for p in positions):
                    vars = [board.get_variable(p) for p in positions]

                    # 创建三连组变量：当且仅当三个位置都是雷时为真
                    b = model.NewBoolVar(f"triple_{pos}_{dx}_{dy}")
                    model.AddBoolAnd(vars).OnlyEnforceIf(b)
                    model.AddBoolOr([v.Not() for v in vars]).OnlyEnforceIf(b.Not())

                    # 记录此三连组覆盖的所有位置
                    for p in positions:
                        position_coverage[p].append(b)

        # 只对雷位置添加约束：必须属于至少一个三连组
        for pos, var in board(mode="variable"):
            coverage_list = position_coverage[pos]

            if coverage_list:  # 确保该位置有三连组覆盖
                # 雷 => 至少属于一个三连组
                model.AddBoolOr(coverage_list).OnlyEnforceIf(var)
                logger.debug(f"Pos {pos}:雷必须属于{len(coverage_list)}个三连组之一")
            else:
                # 无三连组覆盖的位置不能是雷
                model.Add(var == 0)
                logger.warning(f"位置{pos}无三连组覆盖，强制为非雷")

    def check(self, board: 'AbstractBoard') -> bool:
        pass

    @classmethod
    def method_choose(cls) -> int:
        return 1
