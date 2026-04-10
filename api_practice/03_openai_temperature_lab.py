"""
실습 3. temperature 비교하기

학습 목표
1. 같은 질문이라도 temperature 가 다르면 결과가 어떻게 달라지는지 보기
2. 창의적인 작업과 사실 설명 작업의 차이 이해하기

실행:
    python 03_openai_temperature_lab.py
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
QUESTION = TODO
TEMPERATURES = [0.2, TODO, 1.3]


def ask_with_temperature(client: OpenAI, question: str, temperature: float) -> str:
    """
    TODO 1
    temperature 값을 바꿔 가며 응답을 받아오세요.

    힌트:
    - model=MODEL
    - input=question
    - temperature=temperature
    """
    # 예시 뼈대:
    # response = client.responses.create(
    #     model=MODEL,
    #     input=question,
    #     temperature=temperature,
    # )
    # return response.output_text
    raise NotImplementedError("TODO 1: ask_with_temperature 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 3 - temperature 비교")

    missing = check_todo_map({"QUESTION": QUESTION, "TEMPERATURES[1]": TEMPERATURES[1]})
    if missing:
        print_not_ready("실습 3", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()

    print("[질문]")
    print(QUESTION)

    for temperature in TEMPERATURES:
        try:
            print(f"\n--- temperature = {temperature} ---")
            answer = ask_with_temperature(client, QUESTION, float(temperature))
            print(answer)
        except NotImplementedError as exc:
            print_not_ready("실습 3", [str(exc)])
            return
        except Exception as exc:  # pragma: no cover - API/network runtime
            print(f"오류 발생: {exc}")

    print("\n도전 과제")
    print("- 설명형 질문과 창작형 질문 각각에 어울리는 temperature 는 얼마일까요?")
    print("- 0.0 에 가까운 값과 1.5 에 가까운 값의 차이를 말로 정리해 보세요.")


if __name__ == "__main__":
    main()
