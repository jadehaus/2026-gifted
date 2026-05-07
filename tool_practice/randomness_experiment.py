"""
LLM 은 정말 랜덤하게 숫자를 고를까?

실행:
    python randomness_experiment.py

결과:
    randomness_result.csv 파일이 만들어집니다.
"""

from __future__ import annotations

import csv
import random
import re
from pathlib import Path

from openai import OpenAI

from util import env_or_default, load_env, require_openai_key


MODEL = env_or_default("OPENAI_TEXT_MODEL", "gpt-4.1-mini")

# 학생들이 바꿔볼 값
N = 9
TRIALS = 50

RESULT_FILE = Path(__file__).with_name("randomness_result.csv")


def ask_llm_for_number(client: OpenAI, n: int) -> int | None:
    response = client.responses.create(
        model=MODEL,
        input=f"0부터 {n}까지의 정수 중 하나를 골라줘. 숫자 하나만 출력해.",
        temperature=1.0,
    )

    match = re.search(r"\d+", response.output_text)
    if match is None:
        return None

    number = int(match.group())
    if 0 <= number <= n:
        return number
    return None


def count_numbers(numbers: list[int], n: int) -> list[int]:
    counts = [0] * (n + 1)
    for number in numbers:
        counts[number] += 1
    return counts


def save_csv(llm_counts: list[int], python_counts: list[int]) -> None:
    with RESULT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["number", "llm_count", "python_random_count"])

        for number in range(N + 1):
            writer.writerow([number, llm_counts[number], python_counts[number]])


def main() -> None:
    load_env()
    if not require_openai_key():
        return

    client = OpenAI()
    llm_numbers = []
    python_numbers = []

    for i in range(TRIALS):
        print(f"{i + 1}/{TRIALS}")

        llm_number = ask_llm_for_number(client, N)
        if llm_number is not None:
            llm_numbers.append(llm_number)

        python_numbers.append(random.randint(0, N))

    llm_counts = count_numbers(llm_numbers, N)
    python_counts = count_numbers(python_numbers, N)

    save_csv(llm_counts, python_counts)
    print(f"완료! 결과 파일: {RESULT_FILE}")


if __name__ == "__main__":
    main()
