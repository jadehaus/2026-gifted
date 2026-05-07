"""
파일/메모 tool 실습 파일입니다.

추천 질문:
- "내가 좋아하는 음식이 떡볶이라고 저장해줘."
- "내가 저장한 메모 목록을 보여줘."
- "내가 좋아하는 음식이 뭐라고 했지?"
"""

from __future__ import annotations

from pathlib import Path


NOTES_DIR = Path(__file__).with_name("notes")


def save_note(title: str, content: str) -> dict:
    """title 이름으로 content 를 파일에 저장하는 메모 tool 입니다."""
    # TODO: notes 폴더를 만들고, title 에 해당하는 파일에 content 를 저장해 보세요.
    raise NotImplementedError("save_note tool 을 완성해 주세요.")


def load_note(title: str) -> dict:
    """title 이름의 메모 파일을 읽어오는 tool 입니다."""
    # TODO: 저장된 파일을 찾아 내용을 읽어 보세요. 파일이 없을 때도 처리해 보세요.
    raise NotImplementedError("load_note tool 을 완성해 주세요.")


def list_notes() -> list:
    """저장된 메모 제목 목록을 보여주는 tool 입니다."""
    # TODO: notes 폴더 안에 어떤 메모 파일들이 있는지 목록으로 만들어 보세요.
    raise NotImplementedError("list_notes tool 을 완성해 주세요.")


TOOLS = [
    save_note,
    load_note,
    list_notes,
]
