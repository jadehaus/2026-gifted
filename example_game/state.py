from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .game_data import MAP, START_STATE

GAME_DIR = Path(__file__).resolve().parent
SAVE_PATH = GAME_DIR / "saves" / "progress.json"


def new_state() -> dict[str, Any]:
    state = copy.deepcopy(START_STATE)
    state["world_items"] = {room_id: list(room.get("items", [])) for room_id, room in MAP.items()}
    state["defeated_enemies"] = []
    return state


def load_state() -> dict[str, Any]:
    if not SAVE_PATH.exists():
        state = new_state()
        save_state(state)
        return state
    try:
        state = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        state.setdefault("world_items", {room_id: list(room.get("items", [])) for room_id, room in MAP.items()})
        state.setdefault("defeated_enemies", [])
        return state
    except json.JSONDecodeError:
        state = new_state()
        state["journal"].append("손상된 저장 파일을 발견해 새 기록으로 복구했다.")
        save_state(state)
        return state


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def reset_state() -> dict[str, Any]:
    state = new_state()
    save_state(state)
    return state


def current_objective(state: dict[str, Any]) -> str:
    flags = state.get("flags", {})
    if "forgotten_scribe" in state.get("defeated_enemies", []):
        return "동생의 마지막 기록을 되찾았다. 기록관을 빠져나가자."
    if state.get("battle"):
        return "지금은 전투 중. 공격·방어·도구로 적을 물리치자."
    if flags.get("boss_open"):
        return "관측소로 올라가 망각 서기관과 마주하자. 빛에 약한 적이다."
    if flags.get("clock_fixed"):
        return "거울 기록실의 봉인문 수수께끼('세 글자')를 풀자."
    if flags.get("met_sia"):
        return "별자리 시계를 고치자. 청동 톱니를 찾아 '새벽 3시'에 맞춰야 한다."
    return "은빛 로비에서 시아에게 말을 걸고 단서를 모으자."


def public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "player": state["player"],
        "location": state["location"],
        "inventory": state["inventory"],
        "flags": state["flags"],
        "affection": state["affection"],
        "battle": state["battle"],
        "defeated_enemies": state.get("defeated_enemies", []),
        "journal": state["journal"][-8:],
        "turn": state["turn"],
        "objective": current_objective(state),
    }
