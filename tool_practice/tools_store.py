"""
CSV 데이터 tool 실습 파일입니다.

class_store.csv 를 작은 데이터베이스처럼 읽습니다.
엑셀에서 CSV 내용을 바꾸면 tool 결과도 바뀝니다.
"""

from __future__ import annotations

import csv
from pathlib import Path


DATA_FILE = Path(__file__).with_name("class_store.csv")


def read_store_data() -> list:
    """CSV 파일을 읽어서 물건 목록으로 바꿉니다."""
    with DATA_FILE.open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


def search_store_item(keyword: str) -> list:
    """매점/문구점 CSV 데이터에서 keyword 가 들어간 물건을 검색합니다."""
    results = []
    for item in read_store_data():
        if keyword in item["name"] or keyword in item["category"]:
            results.append(item)
    return results


def check_item_stock(item_name: str) -> dict:
    """CSV 데이터에서 물건 이름을 찾아 가격, 재고, 위치를 알려줍니다."""
    for item in read_store_data():
        if item_name in item["name"]:
            return item
    return {"error": f"{item_name} 물건을 찾지 못했습니다."}


def calculate_total_price(item_name: str, count: int) -> dict:
    """CSV 데이터에서 물건 가격을 찾아 count 개를 살 때 총액을 계산합니다."""
    item = check_item_stock(item_name)
    if "error" in item:
        return item

    price = int(item["price"])
    stock = int(item["stock"])

    return {
        "name": item["name"],
        "count": count,
        "price_each": price,
        "total_price": price * count,
        "enough_stock": stock >= count,
        "current_stock": stock,
    }


TOOLS = [
    search_store_item,
    check_item_stock,
    calculate_total_price,
]
