"""
랜덤/시뮬레이션 tool 실습 파일입니다.

추천 질문:
- "주사위 100번 굴려서 6이 몇 번 나왔는지 알려줘."
- "우리 반 발표자 후보 중 한 명을 공정하게 뽑아줘."
- "동전 20번 던진 결과를 표로 보여줘."
"""

from __future__ import annotations


def roll_dice(n: int, sides: int) -> dict:
    """sides 면체 주사위를 n 번 굴리고 결과를 요약하는 tool 입니다."""
    # TODO: random 모듈을 사용해 1부터 sides 사이의 숫자를 n 번 만들어 보세요.
    raise NotImplementedError("roll_dice tool 을 완성해 주세요.")


def flip_coin(n: int) -> dict:
    """동전을 n 번 던지고 앞면/뒷면 횟수를 세는 tool 입니다."""
    # TODO: 앞면과 뒷면 중 하나를 n 번 무작위로 고르게 해 보세요.
    raise NotImplementedError("flip_coin tool 을 완성해 주세요.")


def random_pick(items: str) -> dict:
    """쉼표로 구분된 items 중 하나를 무작위로 고르는 tool 입니다."""
    # TODO: "민지,준호,서연" 같은 문자열을 목록으로 바꾼 뒤 하나를 골라 보세요.
    raise NotImplementedError("random_pick tool 을 완성해 주세요.")


TOOLS = [
    roll_dice,
    flip_coin,
    random_pick,
]
