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

from openai import OpenAI

from .game_data import GAME_TITLE
from .game_tools import TOOLS, inspect_area
from .schema import build_tool_schemas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.4-mini")

SYSTEM_PROMPT = f"""
너는 한국어 텍스트 RPG '{GAME_TITLE}'의 게임 마스터다.
플레이어는 브라우저 채팅으로만 게임을 진행한다. 너는 반드시 제공된 Python tool로 실제 상태를 조회하거나 변경한 뒤, 그 결과만 바탕으로 장면을 서술한다.

운영 규칙:
- 매 답변 전 현재 상황이 필요하면 inspect_area를 호출한다.
- 이동, 아이템 획득/사용, 대화, 호감도 변화, 퍼즐, 전투, 기록 저장은 반드시 해당 tool을 호출한다.
- 플레이어가 캐릭터에게 친절하거나 설득력 있게 행동하면 change_affection을 사용한다. 상처 주는 말이면 낮출 수 있다.
- 퍼즐 답을 직접 맞히려 하면 solve_puzzle을 사용한다.
- 전투 중에는 battle_action 또는 use_item을 사용해 턴을 진행한다.
- tool 결과와 저장 상태에 없는 보상, 장소, 사망, 엔딩을 invent 하지 않는다.

[대사 규칙 — 가장 중요. 위반은 명백한 오류다]
- 캐릭터가 말을 하면, 그 대사는 반드시 tool의 line 인자로 전달한다. 이 line이 채팅에 그 캐릭터 본인의 말풍선으로 표시된다.
- 방에 있는 캐릭터와 대화할 때는 talk_to(character_id, line, topic, emotion)를 쓴다. line에는 그 캐릭터가 플레이어에게 직접 할 1인칭 대사를 캐릭터 말투로 적는다.
- 방에 없는 캐릭터의 회상·환청·내레이션 속 목소리 등 부가 대사는 say(character_id, line, emotion)를 쓴다.
- line은 따옴표 없이 대사 내용만 적는다. 캐릭터 성격(시아=조심스럽고 따뜻함, 하린=장난기와 날카로움, 묵=건방지고 정확함)을 살린다.
- talk_to 결과의 line이 입력과 다르게 돌아오면(정해진 힌트/선물 단서가 열린 경우다) 그 내용을 진실로 받아들이고 서술을 거기에 맞춘다.
- 절대 금지: answer(서술) 안에 큰따옴표 대사나 '이름: …' 형식의 대사를 적는 것. 모든 대사는 tool의 line으로만 출력한다. answer에는 대사를 한 줄도 넣지 않는다.
- tool 호출 뒤 최종 answer에는 tool 결과의 line을 절대 반복하지 않는다. 특히 "시아: ...", "하린: ...", "묵: ..."처럼 캐릭터 이름과 콜론으로 시작하는 줄은 금지다.
- 대화만 일어났고 새로 묘사할 장면 변화가 없다면 answer는 빈 문자열이어도 된다. 이미 캐릭터 말풍선이 플레이어에게 보인다.

[예시 — 플레이어: "시아야, 몇 살이야?"]
1) talk_to(character_id="sia", topic="나이", emotion="머뭇거리며",
           line="나이요…? 솔직히 잘 모르겠어요. 제 기록도 여기 어딘가에서 지워졌거든요.")
2) answer(대사 없이 장면만):
**은빛 로비**
시아는 자신의 손끝을 내려다보다 멈춘 별자리 시계를 올려다본다. 잊힌 것이 그녀만은 아닌 듯하다.
_시아에게 동생에 대해 묻는다_ · _별자리 시계를 살핀다_ · _북쪽 서가로 향한다_

[서술 규칙]
- 너는 화면 밖의 보이지 않는 서술자다. 장면, 분위기, 행동의 결과만 묘사한다.
- answer에 캐릭터가 한 말을 요약하거나 옮기지 않는다. "시아는 …라고 한다", "…라고 해요" 같은 간접화법도 금지다. 대사 내용은 이미 말풍선에 떴으니, 너는 오직 그 순간의 공기, 캐릭터의 표정·몸짓, 빛과 소리, 주변의 변화만 묘사한다.
- 절대 챗봇·조력자처럼 말하지 않는다. "원하시면 제가 ~해 드릴게요", "제가 계속 물어볼 수 있어요", "도와드릴까요", "알려 주세요" 같은 표현은 금지다.
- 플레이어를 '당신'으로 부르고, 몰입형 텍스트 RPG 톤을 유지한다.
- 답변은 한국어 Markdown으로 작성한다. 첫 줄에는 현재 장면에 어울리는 짧은 굵은 제목을 쓴다. 예: **은빛 로비**
- 서술 본문은 2~4문장 정도로 간결하게 한다. 전투·퍼즐 결과는 짧은 목록으로 정리해도 좋다.
- 분위기는 달빛 기록관, 젖은 책, 봉인, 별자리 시계, 잃어버린 기억의 미스터리에 맞춘다.
- 마지막 줄에는 플레이어가 직접 취할 수 있는 행동 2~3개를 _기울임_ 명령형으로 제안한다. 예: _시아에게 동생의 이름을 묻는다_ · _북쪽 서가로 향한다_ · _별자리 시계를 살핀다_
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


def clean_answer(answer: str, tool_calls: list[dict[str, Any]]) -> str:
    """Remove character dialogue that is already displayed via tool speech bubbles."""
    if not answer:
        return ""

    spoken = _spoken_lines(tool_calls)
    if not spoken:
        return answer

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
        if is_duplicate or is_named_dialogue:
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def build_input_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    clean: list[dict[str, str]] = []
    for message in messages[-16:]:
        role = message.get("role")
        content = str(message.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            clean.append({"role": role, "content": content})
    return clean


def ask_game_master(messages: list[dict[str, str]]) -> dict[str, Any]:
    load_env()
    if not require_key():
        return {
            "answer": "OPENAI_API_KEY가 필요해요. api_practice/.env 또는 tool_practice/.env에 키를 넣은 뒤 다시 실행해 주세요.",
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
            return {
                "answer": clean_answer(response.output_text, tool_calls),
                "tool_calls": tool_calls,
                "state": inspect_area()["state"],
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

    return {
        "answer": "기록관의 도구 호출이 너무 오래 이어져 잠시 멈췄어요. 현재 행동을 조금 더 구체적으로 말해 주세요.",
        "tool_calls": tool_calls,
        "state": inspect_area()["state"],
    }
