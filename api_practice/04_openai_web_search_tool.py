"""
실습 4. OpenAI web search tool 사용하기

학습 목표
1. 최신 정보가 필요한 질문 만들기
2. built-in tool 을 모델에 연결하기
3. 검색이 필요한 질문과 필요 없는 질문을 구분하기

실행:
    python 04_openai_web_search_tool.py
"""

from __future__ import annotations

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


MODEL = env_or_default("OPENAI_REASONING_MODEL", "gpt-5-mini")
QUESTION = TODO
SEARCH_CONTEXT_SIZE = TODO


def build_tools() -> list[dict]:
    """
    TODO 1
    web_search_preview 도구 설정을 반환하세요.

    힌트:
    - type: web_search_preview
    - search_context_size: low / medium / high
    """
    # 예시 정답 형태:
    # return [
    #     {
    #         "type": "web_search_preview",
    #         "search_context_size": SEARCH_CONTEXT_SIZE,
    #     }
    # ]
    raise NotImplementedError("TODO 1: build_tools 를 완성하세요.")


def ask_with_search(client: OpenAI, question: str) -> str:
    """
    TODO 2
    tools=build_tools() 를 넣어 responses.create 를 호출하세요.
    """
    # 예시 뼈대:
    # response = client.responses.create(
    #     model=MODEL,
    #     input=question,
    #     tools=build_tools(),
    # )
    # return response.output_text
    raise NotImplementedError("TODO 2: ask_with_search 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 4 - web search tool")

    missing = check_todo_map(
        {
            "QUESTION": QUESTION,
            "SEARCH_CONTEXT_SIZE": SEARCH_CONTEXT_SIZE,
        }
    )
    if missing:
        print_not_ready("실습 4", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()

    print("[질문]")
    print(QUESTION)

    try:
        answer = ask_with_search(client, QUESTION)
        print("\n[응답]")
        print(answer)
    except NotImplementedError as exc:
        print_not_ready("실습 4", [str(exc)])
    except Exception as exc:  # pragma: no cover - API/network runtime
        print("\n실행 중 오류가 발생했습니다.")
        print(exc)

    print("\n도전 과제")
    print("- 질문을 '오늘', '최근', '최신' 이 들어가도록 바꿔 보세요.")
    print("- search_context_size 를 low, medium, high 로 바꿔 결과 차이를 관찰해 보세요.")


if __name__ == "__main__":
    main()
