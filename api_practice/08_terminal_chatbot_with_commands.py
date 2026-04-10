"""
실습 8. 명령어가 있는 터미널 챗봇 만들기

추가 기능
1. /help: 도움말 보기
2. /reset: 대화 기록 초기화
3. /save: 대화 내용을 파일로 저장
4. /exit: 종료

실행:
    python 08_terminal_chatbot_with_commands.py
"""

from __future__ import annotations

from pathlib import Path

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
BOT_NAME = TODO
SYSTEM_PROMPT = TODO
TEMPERATURE = TODO
LOG_DIR = Path(__file__).resolve().parent / "chat_logs"


def build_history() -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_history(history: list[dict]) -> Path:
    LOG_DIR.mkdir(exist_ok=True)
    save_path = LOG_DIR / "last_chat.txt"

    lines = []
    for message in history:
        role = message["role"].upper()
        content = message["content"]
        lines.append(f"[{role}] {content}")

    save_path.write_text("\n".join(lines), encoding="utf-8")
    return save_path


def print_help() -> None:
    print("\n사용 가능한 명령어")
    print("- /help  : 도움말 보기")
    print("- /reset : 지금까지의 대화 초기화")
    print("- /save  : 대화 내용을 파일로 저장")
    print("- /exit  : 챗봇 종료")


def ask_bot(client: OpenAI, history: list[dict]) -> str:
    """
    TODO 1
    chat.completions.create(...) 를 사용해 답변을 만들어 보세요.
    """
    # 예시 뼈대:
    # response = client.chat.completions.create(
    #     model=MODEL,
    #     messages=history,
    #     temperature=float(TEMPERATURE),
    # )
    # return response.choices[0].message.content
    raise NotImplementedError("TODO 1: ask_bot 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 8 - 명령어 지원 터미널 챗봇")

    missing = check_todo_map(
        {
            "BOT_NAME": BOT_NAME,
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "TEMPERATURE": TEMPERATURE,
        }
    )
    if missing:
        print_not_ready("실습 8", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()
    history = build_history()

    print(f"{BOT_NAME} 를 시작합니다. /help 를 입력해 보세요.")

    while True:
        user_input = input("\nYou > ").strip()
        if not user_input:
            print("빈 입력은 건너뜁니다.")
            continue

        if user_input == "/help":
            print_help()
            continue
        if user_input == "/reset":
            history = build_history()
            print("대화 기록을 초기화했습니다.")
            continue
        if user_input == "/save":
            saved_path = save_history(history)
            print(f"대화를 저장했습니다: {saved_path}")
            continue
        if user_input == "/exit":
            print("대화를 종료합니다.")
            break

        history.append({"role": "user", "content": user_input})

        try:
            reply = ask_bot(client, history)
        except NotImplementedError as exc:
            print(f"{BOT_NAME} > 아직 구현 안한 부분이 있군요! {exc}")
            return
        except Exception as exc:  # pragma: no cover - API/network runtime
            print(f"{BOT_NAME} > 오류가 발생했습니다: {exc}")
            continue

        print(f"{BOT_NAME} > {reply}")
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
