"""
실습 7. 터미널에서 연속 대화가 가능한 챗봇 만들기

학습 목표
1. 대화 기록(history) 저장
2. user / assistant 역할 구분
3. /exit 명령으로 종료하기

실행:
    python 07_terminal_chatbot_basic.py
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
TEMPERATURE = 0.7


def build_history() -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def ask_bot(client: OpenAI, history: list[dict]) -> str:
    """
    TODO 1
    chat.completions.create(...) 를 호출해서 마지막 assistant 답변을 반환하세요.

    힌트:
    - model=MODEL
    - messages=history
    - temperature=TEMPERATURE
    """
    # 예시 뼈대:
    # response = client.chat.completions.create(
    #     model=MODEL,
    #     messages=history,
    #     temperature=TEMPERATURE,
    # )
    # return response.choices[0].message.content
    raise NotImplementedError("TODO 1: ask_bot 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 7 - 터미널 챗봇 기본")

    missing = check_todo_map({"SYSTEM_PROMPT": SYSTEM_PROMPT})
    if missing:
        print_not_ready("실습 7", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()
    history = build_history()

    print("챗봇을 시작합니다. 종료하려면 /exit 를 입력하세요.")

    while True:
        user_input = input("\nYou > ").strip()
        if not user_input:
            print("빈 입력은 건너뜁니다.")
            continue
        if user_input == "/exit":
            print("대화를 종료합니다.")
            break

        history.append({"role": "user", "content": user_input})

        try:
            reply = ask_bot(client, history)
        except NotImplementedError as exc:
            print(f"Bot > 아직 구현 안한 부분이 있군요! {exc}")
            return
        except Exception as exc:  # pragma: no cover - API/network runtime
            print(f"Bot > 오류가 발생했습니다: {exc}")
            continue

        print(f"Bot > {reply}")
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
