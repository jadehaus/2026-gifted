"""
실습 6. OpenRouter + Qwen 모델에서 thinking 켜 보기

학습 목표
1. OpenRouter HTTP API 호출
2. Qwen 계열 모델에 reasoning.enabled 전달
3. temperature 와 thinking 을 함께 실험하기

실행:
    python 06_openrouter_qwen_enable_thinking.py
"""

from __future__ import annotations

import os

import requests

from common import (
    TODO,
    banner,
    check_todo_map,
    env_or_default,
    load_env,
    pretty_json,
    print_not_ready,
    require_env,
)


MODEL = env_or_default("OPENROUTER_QWEN_MODEL", "qwen/qwen3-30b-a3b")
QUESTION = TODO
ENABLE_THINKING = TODO
TEMPERATURE = TODO


def build_payload(question: str) -> dict:
    """
    TODO 1
    OpenRouter 에 보낼 JSON payload 를 완성하세요.

    힌트:
    - model
    - messages
    - temperature
    - reasoning: {"enabled": ENABLE_THINKING}
    """
    # 예시 뼈대:
    # return {
    #     "model": MODEL,
    #     "messages": [{"role": "user", "content": question}],
    #     "temperature": TEMPERATURE,
    #     "reasoning": {"enabled": ENABLE_THINKING},
    # }
    raise NotImplementedError("TODO 1: build_payload 를 완성하세요.")


def call_openrouter(question: str) -> str:
    """
    TODO 2
    requests.post(...) 로 OpenRouter API 를 호출하세요.

    URL:
    https://openrouter.ai/api/v1/chat/completions
    """
    # 예시 뼈대:
    # response = requests.post(
    #     "https://openrouter.ai/api/v1/chat/completions",
    #     headers={
    #         "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    #         "Content-Type": "application/json",
    #     },
    #     json=build_payload(question),
    #     timeout=60,
    # )
    # response.raise_for_status()
    # data = response.json()
    # return data["choices"][0]["message"]["content"]
    raise NotImplementedError("TODO 2: call_openrouter 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 6 - OpenRouter Qwen thinking")

    missing = check_todo_map(
        {
            "QUESTION": QUESTION,
            "ENABLE_THINKING": ENABLE_THINKING,
            "TEMPERATURE": TEMPERATURE,
        }
    )
    if missing:
        print_not_ready("실습 6", missing)
        return

    if not require_env("OPENROUTER_API_KEY"):
        return

    try:
        answer = call_openrouter(QUESTION)
        print("\n[응답]")
        print(answer)
    except NotImplementedError as exc:
        print_not_ready("실습 6", [str(exc)])
    except Exception as exc:  # pragma: no cover - API/network runtime
        print("\n실행 중 오류가 발생했습니다.")
        print(exc)

    print("\n도전 과제")
    print("- ENABLE_THINKING 을 True/False 로 바꿔 결과를 비교해 보세요.")
    print("- temperature 를 0.2 와 1.0 으로 바꿔 답변 스타일 차이를 관찰해 보세요.")


if __name__ == "__main__":
    main()
