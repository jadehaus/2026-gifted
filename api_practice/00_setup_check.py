"""
수업 시작 전에 실행하는 환경 점검 스크립트입니다.

실행:
    python 00_setup_check.py
"""

from __future__ import annotations

import importlib
import os

from common import banner, env_or_default, load_env


def check_package(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False


def main() -> None:
    load_env()
    banner("API Practice Setup Check")

    packages = {
        "openai": check_package("openai"),
        "dotenv": check_package("dotenv"),
        "flask": check_package("flask"),
        "requests": check_package("requests"),
    }

    print("[1] 패키지 점검")
    for name, ok in packages.items():
        print(f"- {name}: {'OK' if ok else 'MISSING'}")

    print("\n[2] 환경변수 점검")
    print(f"- OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'EMPTY'}")
    print(f"- OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'EMPTY'}")

    print("\n[3] 기본 모델 이름")
    print(f"- OpenAI text model: {env_or_default('OPENAI_TEXT_MODEL', 'gpt-4.1-mini')}")
    print(f"- OpenAI reasoning model: {env_or_default('OPENAI_REASONING_MODEL', 'gpt-5-mini')}")
    print(f"- OpenRouter Qwen model: {env_or_default('OPENROUTER_QWEN_MODEL', 'qwen/qwen3-30b-a3b')}")

    print("\n[4] 다음 순서 추천")
    print("- 01_openai_basic_response.py")
    print("- 02_openai_reasoning_effort_lab.py")
    print("- 03_openai_temperature_lab.py")
    print("- 04_openai_web_search_tool.py")
    print("- 05_openai_custom_tool.py")
    print("- 06_openrouter_qwen_enable_thinking.py")
    print("- 07_terminal_chatbot_basic.py")
    print("- 08_terminal_chatbot_with_commands.py")
    print("- web_chatbot/app.py")


if __name__ == "__main__":
    main()
