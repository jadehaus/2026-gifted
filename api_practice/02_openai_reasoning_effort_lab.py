"""
실습 2. reasoning effort 비교하기

학습 목표
1. reasoning 모델 호출
2. effort 값을 바꿔 보기
3. 어떤 문제에서 깊게 생각하는 모델이 유리한지 관찰하기

실행:
    python 02_openai_reasoning_effort_lab.py
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


MODEL = env_or_default("OPENAI_REASONING_MODEL", "gpt-5-mini")
QUESTION = TODO
EFFORTS = ["minimal", TODO, "high"]


def ask_with_effort(client: OpenAI, question: str, effort: str) -> str:
    """
    TODO 1
    reasoning={"effort": effort, "summary": "auto"} 를 활용해 응답을 받아오세요.
    """
    # 예시 뼈대:
    # response = client.responses.create(
    #     model=MODEL,
    #     input=question,
    #     reasoning={"effort": effort, "summary": "auto"},
    # )
    # return response.output_text
    raise NotImplementedError("TODO 1: ask_with_effort 를 완성하세요.")


def main() -> None:
    load_env()
    banner("실습 2 - reasoning effort 비교")

    missing = check_todo_map({"QUESTION": QUESTION, "EFFORTS[1]": EFFORTS[1]})
    if missing:
        print_not_ready("실습 2", missing)
        return

    if not require_env("OPENAI_API_KEY"):
        return

    client = OpenAI()

    print("[문제]")
    print(QUESTION)

    for effort in EFFORTS:
        try:
            print(f"\n--- effort = {effort} ---")
            answer = ask_with_effort(client, QUESTION, effort)
            print(answer)
        except NotImplementedError as exc:
            print_not_ready("실습 2", [str(exc)])
            return
        except Exception as exc:  # pragma: no cover - API/network runtime
            print(f"오류 발생: {exc}")

    print("\n도전 과제")
    print("- minimal, medium, high 중 어느 결과가 가장 설득력 있었나요?")
    print("- 답변 길이와 해결 전략이 effort 에 따라 어떻게 달라졌나요?")


if __name__ == "__main__":
    main()
