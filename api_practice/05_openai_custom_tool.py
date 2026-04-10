"""
실습 5. 나만의 tool 연결하기

학습 목표
1. 모델이 함수를 호출하게 만들기
2. Python 함수 결과를 다시 모델에게 전달하기
3. '도구를 쓸지 말지'를 모델이 스스로 판단하는 흐름 이해하기

실행:
    python 05_openai_custom_tool.py
"""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from common import (
    TODO,
    banner,
    check_todo_map,
    env_or_default,
    load_env,
    pretty_json,
    print_not_ready,
    require_env,
    safe_response_text,
)


MODEL = env_or_default("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
QUESTION = TODO

CLASSROOM_DATA = {
    "teacher": "김코딩 선생님",
    "room": "AI 실습실 301호",
    "today_topic": "OpenAI API와 챗봇 만들기",
    "materials": ["노트북", "이어폰", "API 키", "메모장"],
}


def get_classroom_info(category: str) -> dict[str, Any]:
    """학생들이 직접 만든 간단한 로컬 도구."""
    if category == "teacher":
        return {"category": category, "value": CLASSROOM_DATA["teacher"]}
    if category == "room":
        return {"category": category, "value": CLASSROOM_DATA["room"]}
    if category == "today_topic":
        return {"category": category, "value": CLASSROOM_DATA["today_topic"]}
    if category == "materials":
        return {"category": category, "value": CLASSROOM_DATA["materials"]}
    return {
        "category": category,
        "error": "지원하지 않는 category 입니다. teacher, room, today_topic, materials 중 하나를 사용하세요.",
    }


def build_tool_schema() -> list[dict]:
    """
    TODO 1
    function tool 스키마를 완성하세요.

    힌트:
    - tool 이름은 get_classroom_info
    - category 라는 문자열 인자를 받도록 구성
    """
    # 예시 뼈대:
    # return [
    #     {
    #         "type": "function",
    #         "name": "get_classroom_info",
    #         "description": "교실 정보나 준비물을 알려주는 도구",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "category": {
    #                     "type": "string",
    #                     "enum": ["teacher", "room", "today_topic", "materials"],
    #                 }
    #             },
    #             "required": ["category"],
    #             "additionalProperties": False,
    #         },
    #     }
    # ]
    raise NotImplementedError("TODO 1: build_tool_schema 를 완성하세요.")


def find_function_call(response: Any) -> Any | None:
    """response.output 안에서 function_call 항목을 찾습니다."""
    for item in getattr(response, "output", []):
        if getattr(item, "type", "") == "function_call":
            return item
    return None


def run_tool_loop(client: OpenAI, question: str) -> str:
    """
    TODO 2
    1) 모델 첫 호출
    2) function_call 이 나오면 Python 함수 실행
    3) function_call_output 을 다시 보내 최종 답변 받기
    """
    # 예시 흐름:
    # first_response = client.responses.create(
    #     model=MODEL,
    #     input=question,
    #     tools=build_tool_schema(),
    # )
    #
    # tool_call = find_function_call(first_response)
    # if tool_call is None:
    #     return first_response.output_text
    #
    # arguments = json.loads(tool_call.arguments)
    # tool_result = get_classroom_info(arguments["category"])
    #
    # second_response = client.responses.create(
    #     model=MODEL,
    #     previous_response_id=first_response.id,
    #     input=[
    #         {
    #             "type": "function_call_output",
    #             "call_id": tool_call.call_id,
    #             "output": json.dumps(tool_result, ensure_ascii=False),
    #         }
    #     ],
    # )
    # return second_response.output_text
    raise NotImplementedError("TODO 2: run_tool_loop 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 5 - custom tool")

    missing = check_todo_map({"QUESTION": QUESTION})
    if missing:
        print_not_ready("실습 5", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()

    print("[질문]")
    print(QUESTION)

    try:
        answer = run_tool_loop(client, QUESTION)
        print("\n[최종 응답]")
        print(answer)
    except NotImplementedError as exc:
        print_not_ready("실습 5", [str(exc)])
    except Exception as exc:  # pragma: no cover - API/network runtime
        print("\n실행 중 오류가 발생했습니다.")
        print(exc)

    print("\n도전 과제")
    print("- classroom_data 에 snack 이나 homework 를 추가해 보세요.")
    print("- tool description 을 더 자세히 써서 모델이 더 잘 호출하도록 바꿔 보세요.")
    print("- 질문을 바꿔서 모델이 tool 을 호출하지 않는 경우도 실험해 보세요.")


if __name__ == "__main__":
    main()
