"""
숫자 맞히기 게임 tool 실습 파일입니다.

추천 질문:
- "나랑 숫자 맞히기 게임 하자. 네가 게임을 시작해줘."
- "50이라고 추측할게."
- "내 추측이 맞는지 확인해줘."
"""

from __future__ import annotations

from pathlib import Path


GAME_FILE = Path(__file__).with_name("number_game.txt")


def start_game() -> dict:
    """1부터 100 사이의 비밀 숫자를 정하고 게임을 시작하는 tool 입니다."""
    # TODO: 랜덤 숫자를 하나 만들고 파일에 저장해 보세요.
    raise NotImplementedError("start_game tool 을 완성해 주세요.")


def guess(n: int) -> dict:
    """사용자의 추측 n 이 비밀 숫자보다 큰지, 작은지, 정답인지 알려주는 tool 입니다."""
    # TODO: 저장된 비밀 숫자를 읽고 n 과 비교해 보세요.
    raise NotImplementedError("guess tool 을 완성해 주세요.")


def reset_game() -> dict:
    """현재 숫자 맞히기 게임을 초기화하는 tool 입니다."""
    # TODO: 저장된 게임 파일을 지우거나 비워 보세요.
    raise NotImplementedError("reset_game tool 을 완성해 주세요.")


TOOLS = [
    start_game,
    guess,
    reset_game,
]
