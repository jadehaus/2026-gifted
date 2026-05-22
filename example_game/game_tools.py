from __future__ import annotations

from typing import Literal

from .game_data import CHARACTERS, ENEMIES, LORE, MAP, PUZZLES
from .state import load_state, public_state, reset_state, save_state


Direction = Literal["북", "남", "동", "서"]
CharacterId = Literal["sia", "harin", "mook"]
BattleAction = Literal["공격", "방어", "도구", "도망"]


def _room(state: dict) -> dict:
    return MAP[state["location"]]


def _append_journal(state: dict, text: str) -> None:
    if text and (not state["journal"] or state["journal"][-1] != text):
        state["journal"].append(text)


def _level_up_if_needed(state: dict) -> list[str]:
    logs = []
    player = state["player"]
    while player["xp"] >= player["level"] * 10:
        player["xp"] -= player["level"] * 10
        player["level"] += 1
        player["max_hp"] += 6
        player["hp"] = player["max_hp"]
        logs.append(f"{player['name']}의 레벨이 {player['level']}이 되었다. 체력이 모두 회복되었다.")
    return logs


def inspect_area() -> dict:
    """현재 위치, 출구, 캐릭터, 아이템, 퍼즐, 전투 상태를 확인한다. 장면 묘사 전 반드시 사용하기 좋다."""
    state = load_state()
    room = _room(state)
    puzzle = PUZZLES.get(room.get("puzzle")) if room.get("puzzle") else None
    return {
        "state": public_state(state),
        "room": room,
        "visible_puzzle": puzzle,
        "characters": {cid: CHARACTERS[cid] for cid in room.get("characters", [])},
        "room_items": state.get("world_items", {}).get(state["location"], []),
    }


def reset_game() -> dict:
    """저장된 진행 데이터를 초기화하고 새 게임을 시작한다."""
    state = reset_state()
    return {"message": "새 기록을 열었다.", "state": public_state(state), "area": inspect_area()}


def move(direction: Direction) -> dict:
    """지도에서 북/남/동/서 방향으로 이동한다. 잠긴 진행 조건과 전투 상태를 검사한다."""
    state = load_state()
    if state.get("battle"):
        return {"ok": False, "message": "전투 중에는 이동할 수 없다. battle_action을 먼저 사용해야 한다."}

    room = _room(state)
    exits = room.get("exits", {})
    if direction not in exits:
        return {"ok": False, "message": f"{direction}쪽으로 이어지는 길이 없다.", "exits": exits}

    target = exits[direction]
    if target == "observatory" and not state["flags"].get("boss_open"):
        return {"ok": False, "message": "거울 봉인문이 아직 관측소 길을 막고 있다."}

    state["location"] = target
    state["turn"] += 1
    target_room = _room(state)

    enemy_id = target_room.get("battle")
    if enemy_id and state["flags"].get("rune_answered") and enemy_id not in state.get("defeated_enemies", []):
        enemy = ENEMIES[enemy_id]
        state["battle"] = {"enemy_id": enemy_id, "enemy_hp": enemy["hp"], "guarding": False}
        _append_journal(state, f"{enemy['name']}와 전투가 시작되었다.")
    elif target == "west_stacks" and "paper_moth" not in state.get("defeated_enemies", []):
        enemy = ENEMIES["paper_moth"]
        state["battle"] = {"enemy_id": "paper_moth", "enemy_hp": enemy["hp"], "guarding": False}
        _append_journal(state, "서쪽 서가에서 종이 나방이 책장을 뜯어먹고 있었다.")

    save_state(state)
    return {"ok": True, "message": f"{target_room['name']}으로 이동했다.", "area": inspect_area()}


def take_item(item_name: str) -> dict:
    """현재 방에 있는 아이템을 인벤토리에 넣는다."""
    state = load_state()
    room = _room(state)
    world_items = state.setdefault("world_items", {})
    items = world_items.setdefault(state["location"], list(room.get("items", [])))
    if item_name not in items:
        return {"ok": False, "message": f"여기에는 {item_name}이 없다.", "room_items": items}
    items.remove(item_name)
    state["inventory"].append(item_name)
    state["turn"] += 1
    _append_journal(state, f"{room['name']}에서 {item_name}을 얻었다.")
    save_state(state)
    return {"ok": True, "message": f"{item_name}을 얻었다.", "state": public_state(state)}


def use_item(item_name: str, target: str = "") -> dict:
    """인벤토리 아이템을 사용한다. 회복 아이템, 퍼즐 보조, 전투 도구 사용에 쓸 수 있다."""
    state = load_state()
    if item_name not in state["inventory"]:
        return {"ok": False, "message": f"{item_name}은 인벤토리에 없다.", "inventory": state["inventory"]}

    player = state["player"]
    if item_name in {"회복 사탕", "달빛 물약"}:
        amount = 10 if item_name == "회복 사탕" else 16
        player["hp"] = min(player["max_hp"], player["hp"] + amount)
        state["inventory"].remove(item_name)
        state["turn"] += 1
        save_state(state)
        return {"ok": True, "message": f"{item_name}을 사용해 체력을 {amount} 회복했다.", "state": public_state(state)}

    if state.get("battle"):
        return battle_action("도구", item_name)

    return {"ok": True, "message": f"{item_name}을 꺼내 보았다. 직접 효과는 없지만 단서로 쓸 수 있다.", "state": public_state(state)}


def talk_to(character_id: CharacterId, line: str, topic: str = "", emotion: str = "") -> dict:
    """현재 방의 캐릭터와 대화한다.
    line: 그 캐릭터가 지금 플레이어에게 '직접' 할 1인칭 대사. 캐릭터의 성격과 말투를 살려서 네가 작성한다.
          이 문장은 채팅에 캐릭터 본인의 말풍선으로 그대로 표시되므로, 따옴표 없이 대사 내용만 적는다.
    topic: 대화 주제 키워드(예: '나이', '동생', '힌트', '약점'). 호감도/조건에 따라 정해진 단서가 열린다.
    emotion: '조용히', '웃으며' 같은 짧은 어조(선택).
    호감도나 조건이 충족되면 정해진 힌트/선물 대사가 line보다 우선해 표시될 수 있다."""
    state = load_state()
    room = _room(state)
    if character_id not in room.get("characters", []):
        return {"ok": False, "message": "그 캐릭터는 현재 방에 없다.", "present": room.get("characters", [])}

    character = CHARACTERS[character_id]
    affection = state["affection"].get(character_id, 0)
    reward = None
    scripted = None  # 조건이 충족됐을 때만 열리는 정해진 단서 대사

    if affection >= 4 and "bond" in character["dialogue"]:
        scripted = character["dialogue"]["bond"]
    elif character_id == "sia" and (affection >= 2 or "문" in topic or "힌트" in topic):
        scripted = character["dialogue"]["hint"]
    elif character_id == "harin" and affection >= 2 and "달빛 물약" not in state["inventory"]:
        scripted = character["dialogue"]["gift"]
        reward = "달빛 물약"
        state["inventory"].append(reward)
    elif character_id == "mook" and ("약점" in topic or "전투" in topic):
        scripted = character["dialogue"]["weakness"]

    if character_id == "sia":
        state["flags"]["met_sia"] = True

    # 말풍선에 띄울 대사: 조건이 열린 단서가 있으면 그것을, 없으면 GM이 지은 대사를 쓴다.
    spoken = scripted or (line.strip() if line and line.strip() else character["dialogue"]["default"])

    state["turn"] += 1
    _append_journal(state, f"{character['name']}와 대화했다: {topic or '안부'}")
    save_state(state)
    return {
        "ok": True,
        "character": character,
        "affection": affection,
        "line": spoken,
        "emotion": emotion.strip(),
        "scripted": bool(scripted),
        "reward": reward,
        "state": public_state(state),
    }


def say(character_id: CharacterId, line: str, emotion: str = "") -> dict:
    """캐릭터가 직접 말하게 한다. 채팅에 그 캐릭터 본인의 말풍선으로 표시된다.
    모든 캐릭터 대사는 반드시 이 도구로 출력해야 하며, line에는 1인칭 대사만 담는다.
    emotion에는 짧은 어조/표정을 적을 수 있다(예: '조용히', '웃으며')."""
    character = CHARACTERS.get(character_id)
    if not character:
        return {"ok": False, "message": f"{character_id}라는 캐릭터를 찾지 못했다."}
    return {"ok": True, "character": character, "line": line.strip(), "emotion": emotion.strip()}


def change_affection(character_id: CharacterId, amount: int, reason: str) -> dict:
    """동료의 호감도를 조정한다. LLM이 친절한 선택, 무례한 선택, 캐릭터 보호 등을 판단해 사용한다."""
    state = load_state()
    old = state["affection"].get(character_id, 0)
    new = max(-3, min(5, old + amount))
    state["affection"][character_id] = new
    state["turn"] += 1
    _append_journal(state, f"{CHARACTERS[character_id]['name']}의 마음이 움직였다: {reason}")
    save_state(state)
    return {"ok": True, "character": CHARACTERS[character_id]["name"], "old": old, "new": new, "reason": reason}


def solve_puzzle(puzzle_id: Literal["clockwork", "rune_door"], answer: str) -> dict:
    """퍼즐 답이나 해결 행동을 제출한다. 조건, 아이템, 보상을 자동으로 처리한다."""
    state = load_state()
    room = _room(state)
    if room.get("puzzle") != puzzle_id:
        return {"ok": False, "message": "현재 위치의 퍼즐이 아니다.", "current_puzzle": room.get("puzzle")}

    puzzle = PUZZLES[puzzle_id]
    if puzzle.get("required_item") and puzzle["required_item"] not in state["inventory"]:
        return {"ok": False, "message": f"{puzzle['required_item']}이 필요하다."}
    if puzzle.get("required_flag") and not state["flags"].get(puzzle["required_flag"]):
        return {"ok": False, "message": "아직 선행 조건이 해결되지 않았다."}
    if not any(keyword in answer for keyword in puzzle["answer_keywords"]):
        return {"ok": False, "message": "장치가 낮게 울렸지만 열리지 않았다.", "hint": puzzle["description"]}
    if state["flags"].get(puzzle["flag"]):
        return {"ok": True, "message": "이미 해결한 퍼즐이다.", "state": public_state(state)}

    if puzzle.get("required_item") in state["inventory"]:
        state["inventory"].remove(puzzle["required_item"])
    for item in puzzle.get("reward_items", []):
        if item not in state["inventory"]:
            state["inventory"].append(item)
    state["flags"][puzzle["flag"]] = True
    if puzzle.get("opens_flag"):
        state["flags"][puzzle["opens_flag"]] = True
    state["turn"] += 1
    _append_journal(state, puzzle["journal"])
    save_state(state)
    return {"ok": True, "message": f"{puzzle['name']}을 해결했다.", "reward": puzzle.get("reward_items", []), "state": public_state(state)}


def battle_action(action: BattleAction, item_name: str = "") -> dict:
    """전투 턴을 진행한다. 공격, 방어, 도구, 도망 중 하나를 처리하고 적 반격과 보상을 계산한다."""
    state = load_state()
    battle = state.get("battle")
    if not battle:
        return {"ok": False, "message": "현재 전투 중이 아니다."}

    player = state["player"]
    enemy = ENEMIES[battle["enemy_id"]]
    logs = []
    enemy_defeated = False

    if action == "공격":
        damage = 5 + player["level"] * 2
        if enemy["weakness"] in state["inventory"]:
            damage += 3
        battle["enemy_hp"] -= damage
        logs.append(f"{enemy['name']}에게 {damage} 피해를 주었다.")
    elif action == "방어":
        battle["guarding"] = True
        logs.append("자세를 낮춰 다음 피해를 줄였다.")
    elif action == "도구":
        if item_name not in state["inventory"]:
            return {"ok": False, "message": f"{item_name}은 인벤토리에 없다."}
        if item_name == enemy["weakness"]:
            damage = 11
            battle["enemy_hp"] -= damage
            logs.append(f"{item_name}이 약점을 찔러 {damage} 피해를 주었다.")
        elif item_name in {"회복 사탕", "달빛 물약"}:
            amount = 10 if item_name == "회복 사탕" else 16
            player["hp"] = min(player["max_hp"], player["hp"] + amount)
            state["inventory"].remove(item_name)
            logs.append(f"{item_name}을 사용해 체력을 {amount} 회복했다.")
        else:
            logs.append(f"{item_name}을 사용했지만 결정적인 효과는 없었다.")
    elif action == "도망":
        state["battle"] = None
        state["location"] = "lobby"
        state["turn"] += 1
        save_state(state)
        return {"ok": True, "message": "로비까지 물러났다.", "state": public_state(state)}

    if battle["enemy_hp"] <= 0:
        enemy_defeated = True
        state["battle"] = None
        player["xp"] += enemy["xp"]
        if battle["enemy_id"] not in state.setdefault("defeated_enemies", []):
            state["defeated_enemies"].append(battle["enemy_id"])
        for item in enemy.get("loot", []):
            if item not in state["inventory"]:
                state["inventory"].append(item)
        logs.append(f"{enemy['name']}을 물리쳤다. 경험치 {enemy['xp']}을 얻었다.")
        logs.extend(_level_up_if_needed(state))
        if battle["enemy_id"] == "forgotten_scribe":
            _append_journal(state, "망각 서기관을 물리치고 동생의 마지막 기록을 되찾았다. 엔딩에 도달했다.")
    else:
        damage = enemy["attack"]
        if battle.get("guarding"):
            damage = max(1, damage // 2)
            battle["guarding"] = False
        player["hp"] -= damage
        logs.append(f"{enemy['name']}의 반격으로 {damage} 피해를 받았다.")
        if player["hp"] <= 0:
            player["hp"] = max(1, player["max_hp"] // 2)
            state["battle"] = None
            state["location"] = "lobby"
            logs.append("쓰러지기 직전 로비에서 깨어났다. 체력이 절반으로 회복되었다.")
            _append_journal(state, "패배했지만 기록관이 아직 방문자를 놓아주지 않았다.")

    state["turn"] += 1
    save_state(state)
    return {"ok": True, "logs": logs, "enemy_defeated": enemy_defeated, "state": public_state(state)}


def examine(target: str) -> dict:
    """현재 방, 아이템, 사물, 인물을 자세히 살펴 숨은 단서나 묘사를 얻는다."""
    state = load_state()
    room = _room(state)

    if target in {"방", "여기", "주변", room["name"]}:
        return {"ok": True, "target": room["name"], "lore": room["description"]}

    for key, text in LORE.items():
        if key in target or target in key:
            return {"ok": True, "target": key, "lore": text}

    for cid, character in CHARACTERS.items():
        if character["name"] in target or cid == target:
            return {
                "ok": True,
                "target": character["name"],
                "lore": f"{character['role']}. {character['personality']} {character['context']}",
            }

    return {"ok": False, "message": f"'{target}'에서 특별히 눈에 띄는 단서는 없다.", "room": room["description"]}


def add_journal(note: str) -> dict:
    """중요한 추리, 약속, 플레이어 선택을 진행 기록에 저장한다."""
    state = load_state()
    _append_journal(state, note)
    state["turn"] += 1
    save_state(state)
    return {"ok": True, "journal": state["journal"][-8:], "state": public_state(state)}


TOOLS = [
    inspect_area,
    reset_game,
    move,
    take_item,
    use_item,
    talk_to,
    say,
    change_affection,
    solve_puzzle,
    battle_action,
    examine,
    add_journal,
]
