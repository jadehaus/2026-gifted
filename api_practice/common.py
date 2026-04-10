from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - helper fallback
    load_dotenv = None


TODO = "__TODO__"
PROJECT_ROOT = Path(__file__).resolve().parent


def load_env() -> None:
    """Load api_practice/.env if python-dotenv is installed."""
    env_path = PROJECT_ROOT / ".env"
    if load_dotenv is not None:
        load_dotenv(env_path)


def banner(title: str) -> None:
    line = "=" * len(title)
    print(f"\n{line}\n{title}\n{line}")


def is_todo(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return stripped == "" or TODO in stripped or "TODO" == stripped.upper()
    return False


def check_todo_map(items: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for key, value in items.items():
        if is_todo(value):
            missing.append(key)
    return missing


def print_not_ready(task_name: str, missing: list[str] | None = None) -> None:
    print(f"\n[{task_name}] 아직 구현 안 한 부분이 있군요! 구현하고 다시 돌려주세요.")
    if missing:
        print("먼저 채워야 할 항목:")
        for item in missing:
            print(f"- {item}")


def env_or_default(key: str, default: str) -> str:
    value = os.getenv(key)
    if value:
        return value
    return default


def require_env(key: str) -> bool:
    value = os.getenv(key)
    if value:
        return True
    print(f"\n환경변수 {key} 가 비어 있습니다.")
    print("api_practice/.env.example 을 참고해서 .env 파일을 만든 뒤 다시 실행하세요.")
    return False


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def safe_response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text

    choices = getattr(response, "choices", None)
    if choices:
        first = choices[0]
        message = getattr(first, "message", None)
        if message is not None:
            content = getattr(message, "content", None)
            if isinstance(content, str):
                return content

    return "(텍스트 응답을 찾지 못했습니다. 응답 객체를 직접 출력해 보세요.)"
