"""
실습 1. 가장 기본적인 OpenAI 텍스트 생성

학습 목표
1. OpenAI Python SDK 연결
2. 모델 이름과 프롬프트 분리
3. TODO 를 직접 채워서 첫 응답 받기

실행:
    python 01_openai_basic_response.py
"""

from __future__ import annotations

from openai import OpenAI

from common import (
    TODO,
    banner,
    check_todo_map,
    env_or_default,
    load_env,
    print_not_ready,
    require_env,
    safe_response_text,
)


MODEL = env_or_default("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
SYSTEM_PROMPT = TODO
USER_TOPIC = TODO


def build_user_prompt(topic: str) -> str:
    """
    TODO 1
    아래 문자열을 참고해서 topic 을 활용한 사용자 프롬프트를 완성하세요.

    예시:
    - "중학생에게 인공지능을 쉽게 설명해줘."
    - "파이썬 반복문을 예시와 함께 설명해줘."
    """
    # 예시 정답 형태:
    # return f"중학생에게 {topic} 을(를) 쉽게 설명해줘."
    raise NotImplementedError("TODO 1: build_user_prompt 를 완성하세요.")


def call_openai(prompt: str) -> str:
    """
    TODO 2
    client.responses.create(...) 를 호출해 텍스트 응답을 받아오세요.

    힌트:
    - model=MODEL
    - instructions=SYSTEM_PROMPT
    - input=prompt
    """
    client = OpenAI()
    # 예시 뼈대:
    # response = client.responses.create(
    #     model=MODEL,
    #     instructions=SYSTEM_PROMPT,
    #     input=prompt,
    # )
    # return response.output_text
    raise NotImplementedError("TODO 2: call_openai 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 1 - OpenAI 기본 텍스트 생성")

    missing = check_todo_map(
        {
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "USER_TOPIC": USER_TOPIC,
        }
    )
    if missing:
        print_not_ready("실습 1", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    try:
        prompt = build_user_prompt(USER_TOPIC)
        answer = call_openai(prompt)
        print("\n[사용자 프롬프트]")
        print(prompt)
        print("\n[모델 응답]")
        print(answer)
    except NotImplementedError as exc:
        print_not_ready("실습 1", [str(exc)])
    except Exception as exc:  # pragma: no cover - API/network runtime
        print("\n실행 중 오류가 발생했습니다.")
        print(exc)


if __name__ == "__main__":
    main()
