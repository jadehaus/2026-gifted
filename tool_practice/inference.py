"""
OpenAI API 로 tool-using LLM 을 실행하는 아주 작은 파일입니다.

브라우저에서 선택한 tool 함수들을 받아 OpenAI API 에 전달합니다.
"""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from util import (
    build_tool_map,
    build_tool_schemas,
    env_or_default,
    find_function_calls,
    load_env,
    require_openai_key,
    run_python_tool,
)


MODEL = env_or_default("OPENAI_TEXT_MODEL", "gpt-5.4-mini")
SYSTEM_PROMPT = "너는 중학생을 도와주는 친절한 AI야. 필요한 경우 제공된 tool 을 사용해 정확히 답해."


def build_messages(chat_history: str | list[dict[str, str]]) -> list[dict[str, str]]:
    """
    브라우저에서 받은 대화 기록을 OpenAI API 에 줄 messages 리스트로 만듭니다.

    핵심 아이디어:
    - 사용자가 말하면 {"role": "user", "content": "..."} 를 append 합니다.
    - AI 가 답하면 {"role": "assistant", "content": "..."} 를 append 합니다.
    - 다음 질문 때 지금까지 쌓인 messages 전체를 다시 보냅니다.
    """
    messages: list[dict[str, str]] = []

    if isinstance(chat_history, str):
        messages.append({"role": "user", "content": chat_history})
        return messages

    for chat in chat_history:
        role = chat.get("role", "")
        content = str(chat.get("content", "")).strip()

        if role not in {"user", "assistant"}:
            continue
        if not content:
            continue

        messages.append({"role": role, "content": content})

    return messages


def ask_llm(chat_history: str | list[dict[str, str]]) -> dict[str, Any]:
    return ask_llm_with_tools(chat_history, [])


def ask_llm_with_tools(chat_history: str | list[dict[str, str]], tools: list[Any]) -> dict[str, Any]:
    """대화 기록 전체를 받고, tool 이 필요하면 실행한 뒤 최종 답변을 반환합니다."""
    load_env()
    if not require_openai_key():
        return {"answer": "OPENAI_API_KEY 를 먼저 설정해 주세요.", "tool_calls": []}

    client = OpenAI()
    messages = build_messages(chat_history)
    tool_schemas = build_tool_schemas(tools)
    tool_map = build_tool_map(tools)
    tool_calls: list[dict[str, Any]] = []

    request = {
        "model": MODEL,
        "instructions": SYSTEM_PROMPT,
        "input": messages,
    }
    if tool_schemas:
        request["tools"] = tool_schemas

    response = client.responses.create(**request)

    for _ in range(5):
        calls = find_function_calls(response)
        if not calls:
            return {"answer": response.output_text, "tool_calls": tool_calls}

        tool_outputs = []
        for call in calls:
            result = run_python_tool(tool_map, call.name, call.arguments)
            tool_calls.append(
                {
                    "name": call.name,
                    "arguments": json.loads(call.arguments or "{}"),
                    "result": result,
                }
            )
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

        next_request = {
            "model": MODEL,
            "previous_response_id": response.id,
            "input": tool_outputs,
        }
        if tool_schemas:
            next_request["tools"] = tool_schemas

        response = client.responses.create(**next_request)

    return {
        "answer": "tool 호출이 너무 많이 반복되어 멈췄습니다.",
        "tool_calls": tool_calls,
    }


if __name__ == "__main__":
    history: list[dict[str, str]] = []

    while True:
        question = input("You > ").strip()
        if question == "/exit":
            break
        if not question:
            continue

        history.append({"role": "user", "content": question})
        result = ask_llm(history)
        answer = result["answer"]
        print(f"Bot > {answer}")
        history.append({"role": "assistant", "content": answer})
