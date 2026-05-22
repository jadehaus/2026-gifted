from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL_PRACTICE_DIR = PROJECT_ROOT / "tool_practice"

if str(TOOL_PRACTICE_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_PRACTICE_DIR))

from inference import ask_llm_with_tools  # noqa: E402
from util import build_tool_schemas, load_env, pretty_json, require_openai_key  # noqa: E402


app = Flask(__name__)
TOOL_FILE = "my_tools.py"


def load_my_tools() -> list[Any]:
    path = TOOL_PRACTICE_DIR / TOOL_FILE
    module_name = f"web_server_tools_{path.stem}_{path.stat().st_mtime_ns}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{TOOL_FILE} 파일을 읽을 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tools = getattr(module, "TOOLS", [])

    if not isinstance(tools, list):
        raise RuntimeError(f"{TOOL_FILE} 의 TOOLS 는 list 여야 합니다.")

    return tools


def get_tool_payload() -> dict[str, Any]:
    tools = load_my_tools()
    schemas = build_tool_schemas(tools)
    return {
        "selected": TOOL_FILE,
        "schemas": schemas,
        "pretty": pretty_json(schemas),
    }


def clean_chat_messages(messages: Any) -> list[dict[str, str]]:
    clean_messages: list[dict[str, str]] = []

    if not isinstance(messages, list):
        return clean_messages

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = str(message.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            clean_messages.append({"role": role, "content": content})

    return clean_messages


@app.get("/")
def index():
    return render_template("app.html")


@app.get("/api/health")
def health():
    load_env()
    return jsonify({"ok": True, "has_api_key": require_openai_key()})


@app.get("/api/tool-files")
def tool_files():
    return jsonify({"files": [TOOL_FILE], "selected": TOOL_FILE})


@app.get("/api/tools")
def tools():
    try:
        return jsonify(get_tool_payload())
    except Exception as exc:
        return jsonify({"error": str(exc), "selected": TOOL_FILE, "schemas": [], "pretty": "[]"}), 500


@app.post("/api/select-tool-file")
def select_tool_file():
    payload = request.get_json(silent=True) or {}
    filename = str(payload.get("filename", "")).strip()

    if filename not in {"", TOOL_FILE}:
        return jsonify({"error": "web_server는 my_tools.py만 사용할 수 있습니다."}), 400

    try:
        return jsonify(get_tool_payload())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/reset")
def reset():
    return jsonify({"ok": True})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    clean_messages = clean_chat_messages(payload.get("messages", []))

    if not clean_messages:
        return jsonify({"answer": "메시지를 입력해 주세요.", "tool_calls": []})

    try:
        selected_tools = load_my_tools()
        result = ask_llm_with_tools(clean_messages, selected_tools)
        return jsonify(result)
    except Exception as exc:
        return (
            jsonify(
                {
                    "answer": f"서버에서 오류가 발생했어요: {exc}",
                    "tool_calls": [],
                    "error": str(exc),
                }
            ),
            500,
        )


if __name__ == "__main__":
    load_env()
    app.run(host="127.0.0.1", port=5050, debug=True)
