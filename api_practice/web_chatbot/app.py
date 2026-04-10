from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from openai import OpenAI

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

from common import (  # noqa: E402
    TODO,
    check_todo_map,
    env_or_default,
    load_env,
    require_env,
)


load_env()

app = Flask(__name__)
MODEL = env_or_default("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
SYSTEM_PROMPT = TODO
TEMPERATURE = TODO


def build_openai_messages(messages: list[dict]) -> list[dict]:
    normalized = [{"role": "system", "content": SYSTEM_PROMPT}]

    for message in messages:
        role = message.get("role", "user")
        content = str(message.get("content", "")).strip()
        if role not in {"user", "assistant"}:
            continue
        if not content:
            continue
        normalized.append({"role": role, "content": content})

    return normalized


def generate_bot_reply(messages: list[dict]) -> str:
    """
    TODO
    OpenAI chat.completions.create(...) 를 호출해 답변을 반환하세요.

    힌트:
    - client = OpenAI()
    - model=MODEL
    - messages=build_openai_messages(messages)
    - temperature=TEMPERATURE
    """
    # 예시 뼈대:
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model=MODEL,
    #     messages=build_openai_messages(messages),
    #     temperature=float(TEMPERATURE),
    # )
    # return response.choices[0].message.content
    raise NotImplementedError("web_chatbot/app.py 의 generate_bot_reply 를 완성하세요.")


@app.get("/")
def index():
    return render_template("chat.html")


@app.get("/api/health")
def health():
    missing = check_todo_map(
        {
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "TEMPERATURE": TEMPERATURE,
        }
    )
    ready = require_env("OPENAI_API_KEY") and not missing
    return jsonify({"ok": True, "ready": ready, "missing": missing})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages", [])

    missing = check_todo_map(
        {
            "SYSTEM_PROMPT": SYSTEM_PROMPT,
            "TEMPERATURE": TEMPERATURE,
        }
    )

    if missing or not require_env("OPENAI_API_KEY"):
        message = (
            "아직 제가 완성되지 않았어요. "
            "`web_chatbot/app.py` 의 SYSTEM_PROMPT, TEMPERATURE, "
            "`generate_bot_reply()` 를 구현해 주세요."
        )
        return jsonify({"reply": message, "implemented": False, "missing": missing})

    try:
        reply = generate_bot_reply(messages)
        return jsonify({"reply": reply, "implemented": True})
    except NotImplementedError as exc:
        return jsonify({"reply": f"아직 구현 안한 부분이 있군요! {exc}", "implemented": False})
    except Exception as exc:  # pragma: no cover - API/network runtime
        return jsonify({"reply": f"오류가 발생했어요: {exc}", "implemented": True}), 500


if __name__ == "__main__":
    app.run(debug=True)
