"""
보너스 실습 9. 스트리밍 출력 챗봇

학습 목표
1. 답이 한 번에 나오지 않고 조금씩 출력되는 경험 만들기
2. stream=True 형태 익숙해지기

실행:
    python 09_terminal_chatbot_streaming.py
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
)


MODEL = env_or_default("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
SYSTEM_PROMPT = TODO


def build_history() -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def stream_bot_reply(client: OpenAI, history: list[dict]) -> str:
    """
    TODO 1
    stream=True 로 응답을 받아 한 글자씩 또는 조각씩 출력해 보세요.
    마지막에는 전체 문자열을 반환해야 합니다.
    """
    # 예시 흐름:
    # stream = client.chat.completions.create(
    #     model=MODEL,
    #     messages=history,
    #     stream=True,
    # )
    #
    # chunks = []
    # for chunk in stream:
    #     delta = chunk.choices[0].delta.content or ""
    #     print(delta, end="", flush=True)
    #     chunks.append(delta)
    #
    # return "".join(chunks)
    raise NotImplementedError("TODO 1: stream_bot_reply 를 완성하세요.")


def main() -> None:
    load_env()
    banner("보너스 실습 9 - 스트리밍 챗봇")

    missing = check_todo_map({"SYSTEM_PROMPT": SYSTEM_PROMPT})
    if missing:
        print_not_ready("보너스 실습 9", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()
    history = build_history()

    print("스트리밍 챗봇을 시작합니다. 종료하려면 /exit 를 입력하세요.")

    while True:
        user_input = input("\nYou > ").strip()
        if not user_input:
            continue
        if user_input == "/exit":
            print("대화를 종료합니다.")
            break

        history.append({"role": "user", "content": user_input})

        try:
            print("Bot > ", end="", flush=True)
            reply = stream_bot_reply(client, history)
            print()
        except NotImplementedError as exc:
            print(f"아직 구현 안한 부분이 있군요! {exc}")
            return
        except Exception as exc:  # pragma: no cover - API/network runtime
            print(f"\n오류가 발생했습니다: {exc}")
            continue

        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
