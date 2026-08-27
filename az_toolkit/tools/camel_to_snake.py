import re
import sys
from typing import List, Tuple, Union


def camel_to_snake(name: str) -> str:
    """CamelCase -> snake_case"""
    # 先把下划线前后单词单独处理
    parts = name.split('_')
    snake_parts = []
    for part in parts:
        # CamelCase转snake_case
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', part)
        snake = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        snake_parts.append(snake)
    return '_'.join(snake_parts)


def convert_line(line: str, rules: List[Tuple[re.Pattern, Union[int, List[int]]]]) -> str:
    """
    通用行转换函数
    rules: [(pattern, [groups_to_convert]), ...]
    """
    for pattern, groups_to_convert in rules:
        m = pattern.match(line.strip())
        if not m:
            continue

        groups = list(m.groups())

        # 允许 int 或 list[int]
        if isinstance(groups_to_convert, int):
            groups_to_convert = [groups_to_convert]

        # 对指定的 group 做 snake_case 转换
        for idx in groups_to_convert:
            if 0 <= idx < len(groups):
                groups[idx] = camel_to_snake(groups[idx])

        # 重新拼接：把捕获的组按顺序拼接
        return ''.join(groups)
    return line


def convert_block(code_block: str, rules) -> str:
    lines = code_block.strip().splitlines()
    return '\n'.join(convert_line(line, rules) for line in lines)


if __name__ == "__main__":
    # 定义规则
    rules = [
        # 规则1: 匹配 msg.XXX
        (re.compile(r'^(msg\.)([A-Za-z0-9_]+)(.*)$'), 1),
        # 规则2: 匹配 obj.XXX = list.YYY;
        (re.compile(r'^(obj\.)([A-Za-z0-9_]+)(\s*=\s*list\.)([A-Za-z0-9_]+)(;)$'), [1, 3]),
    ]

    print("请输入代码（多行），结束输入 Ctrl+D (Linux/macOS) 或 Ctrl+Z+Enter (Windows):")
    code = sys.stdin.read()
    print("\n转换结果：\n")
    print(convert_block(code, rules))
