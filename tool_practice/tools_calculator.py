"""
계산기 tool 실습 파일입니다.

도입 아이디어:
1. 아무 tool 도 선택하지 않고 큰 곱셈을 물어봅니다.
2. 이 파일을 선택하고 다시 물어봅니다.
3. LLM 이 Python 계산기 tool 을 사용해 정확히 답하는 것을 확인합니다.
"""

from __future__ import annotations


def multiply(a: int, b: int) -> int:
    """두 정수 a 와 b 를 정확히 곱하는 계산기 tool 입니다."""
    return a * b


def add(a: int, b: int) -> int:
    """두 정수 a 와 b 를 정확히 더하는 계산기 tool 입니다."""
    # TODO: 아래 줄을 직접 완성해 보세요.
    raise NotImplementedError("add tool 을 완성해 주세요.")


def subtract(a: int, b: int) -> int:
    """정수 a 에서 정수 b 를 정확히 빼는 계산기 tool 입니다."""
    # TODO: 아래 줄을 직접 완성해 보세요.
    raise NotImplementedError("subtract tool 을 완성해 주세요.")


def divide(a: int, b: int) -> float:
    """정수 a 를 정수 b 로 정확히 나누는 계산기 tool 입니다."""
    # TODO: 아래 줄을 직접 완성해 보세요.
    raise NotImplementedError("divide tool 을 완성해 주세요.")


# TODO: 제곱, 나머지, 몫 같은 새 계산기 tool 도 만들어 보세요.


TOOLS = [
    multiply,
    add,
    subtract,
    divide,
]
