from __future__ import annotations

import threading
import webbrowser

from flask import Flask, jsonify, render_template, request

from .game_data import GAME_TITLE
from .game_tools import TOOLS, inspect_area, reset_game
from .llm_engine import ask_game_master, load_env, require_key
from .schema import build_tool_schemas, pretty_json
from .state import load_state, public_character_history

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title=GAME_TITLE)


@app.route("/api/state", methods=["GET"])
def state():
    return jsonify(inspect_area())


@app.route("/api/characters/history", methods=["GET"])
def character_history():
    return jsonify(public_character_history(load_state()))


@app.route("/api/tools", methods=["GET"])
def tools():
    schemas = build_tool_schemas(TOOLS)
    return jsonify({"schemas": schemas, "pretty": pretty_json(schemas), "count": len(schemas)})


@app.route("/api/health", methods=["GET"])
def health():
    load_env()
    return jsonify({"ok": True, "has_api_key": require_key(), "title": GAME_TITLE})


@app.route("/api/reset", methods=["POST"])
def reset():
    return jsonify(reset_game())


@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages", [])
    if not isinstance(messages, list):
        return jsonify({"answer": "대화 기록 형식이 올바르지 않아요.", "tool_calls": []}), 400
    try:
        return jsonify(ask_game_master(messages))
    except Exception as exc:
        return jsonify({"answer": f"게임 마스터 오류: {exc}", "tool_calls": [], "error": str(exc)}), 500


def open_browser(port: int) -> None:
    webbrowser.open(f"http://127.0.0.1:{port}")


def run(port: int = 5051, open_page: bool = True) -> None:
    load_env()
    if open_page:
        threading.Timer(1.0, open_browser, args=(port,)).start()
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
