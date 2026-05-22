from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .game_data import CHARACTERS, ENEMIES, MAP, START_STATE

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
        history = state.setdefault("character_history", {})
        for character_id in ("sia", "harin", "mook"):
            history.setdefault(character_id, [])
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
    if "forgotten_scribe" in state.get("defeated_enemies", []):
        return "마지막 기록 회수"
    if state.get("battle"):
        return "적 출현"
    return "탐색 중"


def public_battle(state: dict[str, Any]) -> dict[str, Any] | None:
    battle = state.get("battle")
    if not battle:
        return None
    enemy = ENEMIES.get(battle.get("enemy_id"), {})
    return {
        "enemy_id": battle.get("enemy_id"),
        "enemy_name": enemy.get("name", battle.get("enemy_id")),
        "enemy_hp": battle.get("enemy_hp"),
        "guarding": battle.get("guarding", False),
    }


def public_character_history(state: dict[str, Any]) -> dict[str, Any]:
    history = state.get("character_history", {})
    result: dict[str, Any] = {}
    for character_id, character in CHARACTERS.items():
        result[character_id] = {
            "character": {
                "name": character["name"],
                "role": character["role"],
                "emoji": character.get("emoji", ""),
                "accent": character.get("accent", ""),
            },
            "messages": history.get(character_id, [])[-20:],
        }
    return result


def public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "player": state["player"],
        "location": state["location"],
        "inventory": state["inventory"],
        "affection": state["affection"],
        "battle": public_battle(state),
        "defeated_enemies": state.get("defeated_enemies", []),
        "journal": state["journal"][-8:],
        "turn": state["turn"],
        "objective": current_objective(state),
    }
