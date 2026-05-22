from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

from .game_data import GAME_TITLE
from .game_tools import TOOLS, inspect_area
from .schema import build_tool_schemas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.4-mini")

SYSTEM_PROMPT = f"""
너는 한국어 텍스트 RPG '{GAME_TITLE}'의 환경 관찰자다.
너는 세계를 진행하지 않는다. 플레이어가 입력한 단 하나의 행동만 tool로 처리하고, tool 결과로 관찰된 변화만 짧게 보고한다.
게임을 진행하는 데 필요한 최소한의 정보만 말한다.
게임과 관련 없는 정보를 말하지 말고, 게임과 관련 없는 질문은 답하지 마라.

규칙:
- 지도, 퍼즐, 목표, 캐릭터 속마음은 미리 알지 못한다. 필요한 정보는 매번 tool 결과에서만 얻는다.
- 한 입력에 상태 변경 행동은 최대 1개만 수행한다. 이동 후 줍기, 대화 후 조사처럼 이어서 진행하지 않는다.
- 대화는 반드시 talk_to에 player_line을 전달한다. 캐릭터 대사는 별도 LLM이 생성하므로 네가 쓰거나 요약하지 않는다.
- 다음 목표, 선택지, 추천 행동, 공략, 숨은 정답을 말하지 않는다.
- "원하면", "할 수 있어", "다음에는", "중 하나" 같은 안내 문장을 쓰지 않는다.
- 최종 답변은 한국어 0~3문장. 수행한 행동의 결과만 쓴다.
- 대화만 일어났다면 최종 답변은 빈 문자열로 둔다.
- 적이 나타났다면 적이 나타난 분위기만 1~2문장으로 짧게 묘사한 뒤, 반드시 present_enemy_choice tool을 호출한다.
- present_enemy_choice를 호출했다면 최종 답변에 싸운다/도망친다 같은 선택지 텍스트를 쓰지 않는다. 버튼 UI가 선택지를 보여준다.
""".strip()


def load_env() -> None:
    paths = [
        PROJECT_ROOT / "api_practice" / ".env",
        PROJECT_ROOT / "tool_practice" / ".env",
        PROJECT_ROOT / ".env",
    ]
    for path in paths:
        if load_dotenv is not None:
            load_dotenv(path)
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _tool_map() -> dict[str, Any]:
    return {tool.__name__: tool for tool in TOOLS}


def _find_function_calls(response: Any) -> list[Any]:
    return [
        item
        for item in getattr(response, "output", [])
        if getattr(item, "type", None) == "function_call"
    ]


def _run_tool(name: str, arguments_json: str) -> Any:
    tools = _tool_map()
    if name not in tools:
        return {"error": f"{name} tool을 찾지 못했다."}
    try:
        arguments = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return {"error": "tool arguments가 올바른 JSON이 아니다.", "raw": arguments_json}
    try:
        return tools[name](**arguments)
    except Exception as exc:
        return {"error": f"{name} 실행 중 오류", "message": str(exc)}


def _normalize_dialogue(text: str) -> str:
    text = re.sub(r"^[\s>*_`#-]+", "", str(text or "").strip())
    text = re.sub(r"^[가-힣A-Za-z0-9_ -]{1,20}\s*[:：]\s*", "", text)
    text = text.strip().strip("\"'“”‘’")
    text = re.sub(r"\s+", " ", text)
    return text


def _spoken_lines(tool_calls: list[dict[str, Any]]) -> list[dict[str, str]]:
    spoken: list[dict[str, str]] = []
    for call in tool_calls:
        if call.get("name") not in {"talk_to", "say"}:
            continue
        result = call.get("result") or {}
        if not result.get("ok") or not result.get("line"):
            continue
        character = result.get("character") or {}
        spoken.append(
            {
                "name": str(character.get("name") or ""),
                "line": str(result.get("line") or ""),
                "normalized": _normalize_dialogue(str(result.get("line") or "")),
            }
        )
    return spoken


def _has_battle_state(value: Any) -> bool:
    if isinstance(value, dict):
        if value.get("battle"):
            return True
        return any(_has_battle_state(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_battle_state(item) for item in value)
    return False


def _battle_choice_text(tool_calls: list[dict[str, Any]]) -> str:
    def find_battle(value: Any) -> dict[str, Any] | None:
        if isinstance(value, dict):
            battle = value.get("battle")
            if isinstance(battle, dict):
                return battle
            for item in value.values():
                found = find_battle(item)
                if found:
                    return found
        if isinstance(value, list):
            for item in value:
                found = find_battle(item)
                if found:
                    return found
        return None

    battle = find_battle([call.get("result") for call in tool_calls]) or {}
    enemy_name = battle.get("enemy_name") or battle.get("enemy_id") or "적"
    last = str(enemy_name)[-1]
    subject_particle = "이" if "가" <= last <= "힣" and (ord(last) - 0xAC00) % 28 else "가"
    return f"{enemy_name}{subject_particle} 앞을 막고 있다. 싸울지 도망갈지 정해야 한다.\n\n- 싸운다\n- 도망친다"


def _area_with_enemy_choice(tool_calls: list[dict[str, Any]]) -> dict[str, Any]:
    """Ensure the frontend gets the enemy-choice UI event whenever battle is active."""
    area = inspect_area()
    state = area.get("state", {})
    if not state.get("battle"):
        return area
    if any(call.get("name") == "present_enemy_choice" for call in tool_calls):
        return area

    result = _run_tool("present_enemy_choice", "{}")
    if isinstance(result, dict) and result.get("ok"):
        tool_calls.append({"name": "present_enemy_choice", "arguments": {}, "result": result})
    return area


def clean_answer(answer: str, tool_calls: list[dict[str, Any]]) -> str:
    """Remove character dialogue that is already displayed via tool speech bubbles."""
    battle_present = _has_battle_state([call.get("result") for call in tool_calls])
    enemy_choice_presented = any(call.get("name") == "present_enemy_choice" for call in tool_calls)
    if not answer:
        return "" if enemy_choice_presented else (_battle_choice_text(tool_calls) if battle_present else "")

    state_changing_calls = [
        call
        for call in tool_calls
        if call.get("name") not in {"inspect_area", "examine", "present_enemy_choice"}
    ]
    if state_changing_calls and all(call.get("name") == "talk_to" for call in state_changing_calls):
        return ""

    spoken = _spoken_lines(tool_calls)

    cleaned_lines: list[str] = []
    for line in str(answer).splitlines():
        stripped = line.strip()
        normalized = _normalize_dialogue(stripped)
        is_duplicate = any(
            normalized and item["normalized"] and normalized == item["normalized"]
            for item in spoken
        )
        is_named_dialogue = any(
            item["name"] and re.match(rf"^\s*{re.escape(item['name'])}\s*[:：]", stripped)
            for item in spoken
        )
        is_choice_line = (
            (not battle_present or enemy_choice_presented)
            and bool(re.fullmatch(r"(?:[_*][^_*]{2,60}[_*]\s*[·/|,]?\s*){2,}", stripped))
        )
        plain_choice = stripped.lstrip("-*0123456789. ").strip()
        is_text_battle_ui = enemy_choice_presented and (
            "전투 중" in stripped
            or plain_choice in {"공격", "방어", "도구 사용", "도망", "싸운다", "도망친다"}
        )
        if is_duplicate or is_named_dialogue or is_choice_line or is_text_battle_ui:
            continue
        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()
    if battle_present and not enemy_choice_presented and ("싸" not in cleaned or "도망" not in cleaned):
        fallback = _battle_choice_text(tool_calls)
        return f"{cleaned}\n\n{fallback}".strip() if cleaned else fallback
    return cleaned


def build_input_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    clean: list[dict[str, str]] = []
    for message in messages[-6:]:
        role = message.get("role")
        content = str(message.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            clean.append({"role": role, "content": content[:700]})
    return clean


def ask_game_master(messages: list[dict[str, str]]) -> dict[str, Any]:
    load_env()
    if not require_key():
        return {
            "answer": "OPENAI_API_KEY가 필요해요. api_practice/.env 또는 tool_practice/.env에 키를 넣은 뒤 다시 실행해 주세요.",
            "tool_calls": [],
            "state": inspect_area()["state"],
        }
    if OpenAI is None:
        return {
            "answer": "openai 패키지가 필요해요. 프로젝트 환경에 의존성을 설치한 뒤 다시 실행해 주세요.",
            "tool_calls": [],
            "state": inspect_area()["state"],
        }

    client = OpenAI()
    tool_schemas = build_tool_schemas(TOOLS)
    tool_calls: list[dict[str, Any]] = []

    response = client.responses.create(
        model=os.getenv("OPENAI_TEXT_MODEL", MODEL),
        instructions=SYSTEM_PROMPT,
        input=build_input_messages(messages),
        tools=tool_schemas,
    )

    for _ in range(8):
        calls = _find_function_calls(response)
        if not calls:
            area = _area_with_enemy_choice(tool_calls)
            return {
                "answer": clean_answer(response.output_text, tool_calls),
                "tool_calls": tool_calls,
                "state": area["state"],
            }

        outputs = []
        for call in calls:
            result = _run_tool(call.name, call.arguments)
            tool_calls.append(
                {
                    "name": call.name,
                    "arguments": json.loads(call.arguments or "{}"),
                    "result": result,
                }
            )
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

        response = client.responses.create(
            model=os.getenv("OPENAI_TEXT_MODEL", MODEL),
            previous_response_id=response.id,
            input=outputs,
            tools=tool_schemas,
        )

    area = _area_with_enemy_choice(tool_calls)
    return {
        "answer": "기록관의 도구 호출이 너무 오래 이어져 잠시 멈췄어요. 현재 행동을 조금 더 구체적으로 말해 주세요.",
        "tool_calls": tool_calls,
        "state": area["state"],
    }
