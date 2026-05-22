from __future__ import annotations

import inspect
import json
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

try:
    from types import UnionType
except ImportError:  # pragma: no cover
    UnionType = Union


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def python_type_to_json_schema(annotation: Any) -> dict[str, Any]:
    if annotation is inspect._empty:
        return {"type": "string"}
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Literal:
        values = list(args)
        schema = python_type_to_json_schema(type(values[0]) if values else str)
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
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, parameter in signature.parameters.items():
        annotation = type_hints.get(name, parameter.annotation)
        properties[name] = python_type_to_json_schema(annotation)
        if parameter.default is inspect._empty:
            required.append(name)
        else:
            properties[name]["default"] = parameter.default
    return {
        "type": "function",
        "name": func.__name__,
        "description": inspect.getdoc(func) or f"{func.__name__} tool",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


def build_tool_schemas(functions: list[Any]) -> list[dict[str, Any]]:
    return [function_to_tool_schema(func) for func in functions]

