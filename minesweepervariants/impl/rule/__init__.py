#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/06/03 04:23
# @Author  : Wu_RH
# @FileName: __init__.py

import os
import ast
from typing import Dict, Union


def extract_module_docstring(filepath) -> Union[Dict, None]:
    if "sharp" in filepath:
        print(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception:
        return None

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None

    module_doc = ast.get_docstring(tree)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        bases_info = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases_info.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases_info.append(base.attr)
            else:
                bases_info.append(str(base))

        x = 0
        if any("Mines" in b for b in bases_info):
            x |= 1
        if any("MinesClue" in b for b in bases_info):
            x |= 2
        if any("Clue" in b for b in bases_info):
            x |= 4

        if x == 6:
            x = 2

        info = {}
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if (
                        isinstance(target, ast.Name) and target.id == "name" and
                        (isinstance(stmt.value, ast.Str) or
                         isinstance(stmt.value, ast.List) or
                         isinstance(stmt.value, ast.Tuple))
                    ):
                        # 处理字符串列表的情况
                        if (
                            isinstance(stmt.value, ast.List) or
                            isinstance(stmt.value, ast.Tuple)
                        ):
                            # 提取列表中的第一个字符串作为名称
                            name_vals = []
                            for elt in stmt.value.elts:
                                if isinstance(elt, ast.Str) and elt.s.strip():
                                    name_val = elt.s.strip()
                                    name_vals.append(name_val)
                            info["x"] = x
                            info["module_doc"] = module_doc
                            info["names"] = name_vals
                        # 处理单个字符串的情况
                        elif isinstance(stmt.value, ast.Str) and stmt.value.s.strip():
                            name_val = stmt.value.s.strip()
                            info["x"] = x
                            info["module_doc"] = module_doc
                            info["names"] = [name_val]
                    if (
                        isinstance(target, ast.Name) and
                        target.id == "doc" and
                        isinstance(stmt.value, ast.Str)
                    ):
                        # 处理单个字符串的情况
                        doc_val = stmt.value.s.strip()
                        info["doc"] = doc_val
        if "names" in info:
            return info
    return None


def scan_module_docstrings(directory):
    results = []
    for root, _, files in os.walk(directory):
        for name in files:
            if name.endswith('.py'):
                path = os.path.join(root, name)
                pck = extract_module_docstring(path)
                if pck is None:
                    continue
                m_doc = pck.get('module_doc', "")
                x = pck.get('x', 0)
                names = pck.get('names', [])
                doc = pck.get('doc', "")
                results.append((m_doc, doc, x, names))
    return results


def get_all_rules():
    results = {"R": {}, "M": {}, "L": {}, "O": {}}
    dir_path = os.path.dirname(os.path.abspath(__file__))
    for m_doc, doc, x, names in scan_module_docstrings(dir_path):
        if not names:
            continue
        name, names = names[0], names[1:]
        rule_line = None
        if x == 1:
            rule_line = "L"
        elif x == 2:
            rule_line = "M"
        elif x == 4:
            rule_line = "R"
        if rule_line is None:
            continue
        results[rule_line][name] = {
            "names": names,
            "doc": doc,
            "module_doc": m_doc,
        }
    return results
