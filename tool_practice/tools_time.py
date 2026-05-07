"""
시간/날짜 tool 실습 파일입니다.

추천 질문:
- "지금 서울은 몇 시야?"
- "내 생일 2026-09-12까지 며칠 남았어?"
- "오늘부터 100일 뒤는 무슨 요일이야?"
"""

from __future__ import annotations


def get_current_time(timezone: str) -> dict:
    """timezone 지역의 현재 날짜와 시간을 알려주는 tool 입니다."""
    # TODO: datetime 모듈과 zoneinfo 모듈을 사용해 현재 시간을 구해 보세요.
    # 예: timezone 에는 "Asia/Seoul", "UTC", "America/New_York" 같은 값이 들어올 수 있습니다.
    raise NotImplementedError("get_current_time tool 을 완성해 주세요.")


def days_between(date1: str, date2: str) -> dict:
    """YYYY-MM-DD 형식의 두 날짜 사이가 며칠인지 계산하는 tool 입니다."""
    # TODO: 문자열을 날짜로 바꾼 뒤 두 날짜의 차이를 계산해 보세요.
    raise NotImplementedError("days_between tool 을 완성해 주세요.")


def add_days(date: str, n: int) -> dict:
    """YYYY-MM-DD 형식의 날짜에서 n 일 뒤 날짜와 요일을 계산하는 tool 입니다."""
    # TODO: 날짜에 며칠을 더하는 방법을 찾아 구현해 보세요.
    raise NotImplementedError("add_days tool 을 완성해 주세요.")


TOOLS = [
    get_current_time,
    days_between,
    add_days,
]
