"""
나만의 tool 직접 구현하기
"""

from __future__ import annotations


# 예시:
#
# def say_hello(name: str) -> str:
#     """이름을 받아서 반갑게 인사하는 tool 입니다."""
#     return f"{name}님, 안녕하세요!"
#
#
# TOOLS = [
#     say_hello,
# ]


def calculator(expression: str) -> str:
    """Python eval 로 계산식을 실행해 정확한 계산 결과를 반환하는 tool 입니다."""
    return str(eval(expression, {"__builtins__": {}}, {}))


TOOLS = [
    calculator,
]
