from __future__ import annotations

import importlib.util
import threading
import webbrowser
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from inference import ask_llm_with_tools
from util import build_tool_schemas, load_env, pretty_json, require_openai_key


app = Flask(__name__)
PRACTICE_DIR = Path(__file__).resolve().parent
selected_tool_file: str | None = None
selected_tools: list[Any] = []


def list_tool_files() -> list[str]:
    files = ["my_tools.py"]
    files.extend(path.name for path in sorted(PRACTICE_DIR.glob("tools_*.py")))
    return files


def is_allowed_tool_file(filename: str) -> bool:
    return filename in list_tool_files()


def load_tools_from_file(filename: str) -> list[Any]:
    path = PRACTICE_DIR / filename
    module_name = f"student_tools_{path.stem}_{id(path)}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{filename} 파일을 읽을 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tools = getattr(module, "TOOLS", [])

    if not isinstance(tools, list):
        raise RuntimeError(f"{filename} 의 TOOLS 는 list 여야 합니다.")

    return tools


@app.get("/")
def index():
    return render_template("app.html")


@app.get("/api/tool-files")
def tool_files():
    return jsonify({"files": list_tool_files(), "selected": selected_tool_file})


@app.post("/api/select-tool-file")
def select_tool_file():
    global selected_tool_file, selected_tools

    payload = request.get_json(silent=True) or {}
    filename = str(payload.get("filename", "")).strip()

    if filename == "":
        selected_tool_file = None
        selected_tools = []
        return jsonify(
            {
                "selected": selected_tool_file,
                "schemas": [],
                "pretty": pretty_json([]),
            }
        )

    if not is_allowed_tool_file(filename):
        return jsonify({"error": "선택할 수 없는 tool 파일입니다."}), 400

    try:
        tools = load_tools_from_file(filename)
        schemas = build_tool_schemas(tools)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    selected_tool_file = filename
    selected_tools = tools

    return jsonify(
        {
            "selected": selected_tool_file,
            "schemas": schemas,
            "pretty": pretty_json(schemas),
        }
    )


@app.get("/api/tools")
def tools():
    schemas = build_tool_schemas(selected_tools)
    return jsonify(
        {
            "selected": selected_tool_file,
            "schemas": schemas,
            "pretty": pretty_json(schemas),
        }
    )


@app.get("/api/health")
def health():
    load_env()
    return jsonify({"ok": True, "has_api_key": require_openai_key()})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages", [])
    clean_messages = []

    for message in messages:
        role = message.get("role")
        content = str(message.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            clean_messages.append({"role": role, "content": content})

    if not clean_messages:
        return jsonify({"answer": "메시지를 입력해 주세요.", "tool_calls": []})

    try:
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


def open_browser() -> None:
    webbrowser.open("http://127.0.0.1:5050")


if __name__ == "__main__":
    load_env()
    threading.Timer(1.0, open_browser).start()
    app.run(host="127.0.0.1", port=5050, debug=True, use_reloader=False)
