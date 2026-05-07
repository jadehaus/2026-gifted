from __future__ import annotations

import inspect
import json
import os
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

try:
    from types import UnionType
except ImportError:  # Python 3.9 이하에서는 int | None 문법이 없습니다.
    UnionType = Union

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRACTICE_DIR = Path(__file__).resolve().parent


def load_env() -> None:
    """api_practice/.env 또는 tool_practice/.env 에 있는 API 키를 불러옵니다."""
    env_paths = [
        PROJECT_ROOT / "api_practice" / ".env",
        PRACTICE_DIR / ".env",
    ]

    if load_dotenv is None:
        for env_path in env_paths:
            load_env_file_by_hand(env_path)
        return

    for env_path in env_paths:
        load_dotenv(env_path)
        load_env_file_by_hand(env_path)


def load_env_file_by_hand(env_path: Path) -> None:
    """
    아주 단순한 .env 파일을 직접 읽습니다.

    수업 환경마다 python-dotenv 설치 상태가 다를 수 있어서,
    OPENAI_API_KEY=... 같은 기본 형식은 이 함수만으로도 읽히게 해 둡니다.
    """
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def env_or_default(key: str, default: str) -> str:
    return os.getenv(key) or default


def require_openai_key() -> bool:
    if os.getenv("OPENAI_API_KEY"):
        return True
    print("OPENAI_API_KEY 가 비어 있습니다. api_practice/.env 또는 tool_practice/.env 를 확인하세요.")
    return False


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def python_type_to_json_schema(annotation: Any) -> dict[str, Any]:
    """
    Python 타입 힌트를 OpenAI tool schema 에 들어갈 JSON schema 로 바꿉니다.

    예:
    - name: str  -> {"type": "string"}
    - count: int -> {"type": "integer"}
    - mood: Literal["happy", "sad"] -> {"type": "string", "enum": ["happy", "sad"]}
    """
    if annotation is inspect._empty:
        return {"type": "string"}

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Literal:
        values = list(args)
        value_type = type(values[0]) if values else str
        schema = python_type_to_json_schema(value_type)
        schema["enum"] = values
        return schema

    if origin in {Union, UnionType}:
        real_args = [arg for arg in args if arg is not type(None)]
        if len(real_args) == 1:
            return python_type_to_json_schema(real_args[0])

    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation in {list, tuple} or origin in {list, tuple}:
        item_type = args[0] if args else str
        return {"type": "array", "items": python_type_to_json_schema(item_type)}
    if annotation is dict or origin is dict:
        return {"type": "object"}

    return {"type": "string"}


def function_to_tool_schema(func: Any) -> dict[str, Any]:
    """Python 함수 하나를 LLM 이 이해하는 function tool schema 로 바꿉니다."""
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for name, parameter in signature.parameters.items():
        annotation = type_hints.get(name, parameter.annotation)
        properties[name] = python_type_to_json_schema(annotation)

        if parameter.default is not inspect._empty:
            properties[name]["default"] = parameter.default
        else:
            required.append(name)

    description = inspect.getdoc(func) or f"{func.__name__} tool"

    return {
        "type": "function",
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


def build_tool_schemas(functions: list[Any]) -> list[dict[str, Any]]:
    return [function_to_tool_schema(func) for func in functions]


def build_tool_map(functions: list[Any]) -> dict[str, Any]:
    return {func.__name__: func for func in functions}


def run_python_tool(tool_map: dict[str, Any], name: str, arguments_json: str) -> Any:
    """모델이 요청한 tool 이름과 JSON 인자를 받아 실제 Python 함수를 실행합니다."""
    if name not in tool_map:
        return {"error": f"{name} 이라는 tool 을 찾지 못했습니다."}

    try:
        arguments = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return {"error": "tool arguments 가 올바른 JSON 이 아닙니다.", "raw": arguments_json}

    try:
        return tool_map[name](**arguments)
    except Exception as exc:
        return {
            "error": f"{name} tool 실행 중 오류가 발생했습니다.",
            "message": str(exc),
        }


def find_function_calls(response: Any) -> list[Any]:
    """Responses API 결과에서 function_call 항목만 골라냅니다."""
    return [
        item
        for item in getattr(response, "output", [])
        if getattr(item, "type", None) == "function_call"
    ]
