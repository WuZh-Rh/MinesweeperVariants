#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/07 16:43
# @Author  : Wu_RH
# @FileName: connect.py
from typing import List, Callable, Union

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar

from ....abs.board import AbstractBoard, AbstractPosition


def connect(
        model: cp_model.CpModel,
        board: AbstractBoard,
        switch: IntVar,     # 连通性选择
        ub=False,  # 可达处的上限
        connect_value=1,  # 1=雷连通，0=非雷连通
        nei_value: Union[int, tuple, Callable] = 2,  # 1=四连通，2=八连通
        root_vars: List[IntVar] = None,  # 允许提供根节点变量
        positions_vars: List[tuple[AbstractPosition, IntVar]] = None,
):
    # 获取题板上所有位置及其对应的布尔变量
    if positions_vars is None:
        positions_vars = [(pos, var) for pos, var in board("always", mode="variable")]
    if not positions_vars:
        return

    pos_list, var_list = zip(*positions_vars)
    n = len(pos_list)

    # 定义reach_vars整数变量
    reach_vars = [model.NewIntVar(0, (ub if ub else n + 1), f'reach_{i}') for i in range(n)]

    # 定义root_vars布尔变量
    if root_vars is None:
        root_vars = [model.NewBoolVar(f'root_{i}') for i in range(n)]
        model.Add(sum(root_vars) == 1).OnlyEnforceIf(switch)

    for i in range(n):
        # 根据connect_value决定连通对象
        if connect_value == 1:  # 雷连通
            model.AddImplication(root_vars[i], var_list[i]).OnlyEnforceIf(switch)
            model.Add(reach_vars[i] == 1).OnlyEnforceIf([root_vars[i], switch])
            model.Add(reach_vars[i] != 1).OnlyEnforceIf([root_vars[i].Not(), switch])
            model.Add(reach_vars[i] == 0).OnlyEnforceIf([var_list[i].Not(), switch])
        else:  # 非雷连通
            model.AddImplication(root_vars[i], var_list[i].Not()).OnlyEnforceIf(switch)
            model.Add(reach_vars[i] == 1).OnlyEnforceIf([root_vars[i], switch])
            model.Add(reach_vars[i] != 1).OnlyEnforceIf([root_vars[i].Not(), switch])
            model.Add(reach_vars[i] == 0).OnlyEnforceIf([var_list[i], switch])

    # 构造邻接列表（根据nei_value决定连通方式）
    adj = [[] for _ in range(n)]
    for i, pos_i in enumerate(pos_list):
        for j, pos_j in enumerate(pos_list):
            if i != j and board.in_bounds(pos_j):
                # 根据nei_value判断连通方式
                if callable(nei_value):
                    is_neighbor = pos_j in nei_value(pos_i)
                elif type(nei_value) is int:  # 四连通
                    is_neighbor = pos_j in pos_i.neighbors(nei_value)
                elif type(nei_value) is tuple:  # 四连通
                    is_neighbor = pos_j in pos_i.neighbors(nei_value[0], nei_value[1])
                else:  # 八连通
                    raise ValueError("")
                if is_neighbor:
                    adj[i].append(j)

    # 传播约束
    for i in range(n):
        # 条件判断根据connect_value变化
        if connect_value == 1:  # 雷连通
            cond = [var_list[i], root_vars[i].Not()]
        else:  # 非雷连通
            cond = [var_list[i].Not(), root_vars[i].Not()]

        possible_sources = []
        for j in adj[i]:
            tmp = model.NewBoolVar(f'path_{j}_to_{i}')
            model.Add(reach_vars[i] == reach_vars[j] + 1).OnlyEnforceIf([tmp, switch])

            # 根据connect_value决定传播条件
            if connect_value == 1:
                model.AddImplication(tmp, var_list[j]).OnlyEnforceIf(switch)
            else:
                model.AddImplication(tmp, var_list[j].Not()).OnlyEnforceIf(switch)

            is_reach_j_pos = model.NewBoolVar(f'is_reach_pos_{j}')
            model.Add(reach_vars[j] > 0).OnlyEnforceIf([is_reach_j_pos, switch])
            model.Add(reach_vars[j] == 0).OnlyEnforceIf([is_reach_j_pos.Not(), switch])
            model.AddImplication(tmp, is_reach_j_pos).OnlyEnforceIf(switch)

            possible_sources.append(tmp)

        if possible_sources:
            model.AddBoolOr(possible_sources).OnlyEnforceIf(cond + [switch])

    # 最终约束
    for i in range(n):
        if connect_value == 1:  # 雷连通
            model.Add(reach_vars[i] > 0).OnlyEnforceIf([var_list[i], switch])
            model.Add(reach_vars[i] == 0).OnlyEnforceIf([var_list[i].Not(), switch])
        else:  # 非雷连通
            model.Add(reach_vars[i] > 0).OnlyEnforceIf([var_list[i].Not(), switch])
            model.Add(reach_vars[i] == 0).OnlyEnforceIf([var_list[i], switch])
