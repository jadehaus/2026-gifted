"""
한국어 위키피디아 검색 tool 실습 파일입니다.

무료이고 API 키가 필요 없어서, 실제 검색 tool 과 비슷한 경험을 만들기 좋습니다.
"""

from __future__ import annotations

import requests


def search_wikipedia(query: str, max_chars: int = 6000) -> dict:
    """한국어 위키피디아에서 query 를 검색하고, 가장 관련 있는 문서의 본문 텍스트를 가져옵니다."""
    headers = {
        "User-Agent": "middle-school-tool-practice/1.0",
    }

    search_response = requests.get(
        "https://ko.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
        },
        headers=headers,
        timeout=10,
    )
    search_response.raise_for_status()
    search_data = search_response.json()
    search_results = search_data["query"]["search"]

    if not search_results:
        return {"error": f"{query} 검색 결과를 찾지 못했습니다."}

    title = search_results[0]["title"]

    page_response = requests.get(
        "https://ko.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "extracts",
            "explaintext": True,
            "redirects": True,
            "titles": title,
            "format": "json",
        },
        headers=headers,
        timeout=10,
    )
    page_response.raise_for_status()
    page_data = page_response.json()
    pages = page_data["query"]["pages"]
    page = next(iter(pages.values()))
    full_text = page.get("extract", "")
    trimmed_text = full_text[:max_chars]

    return {
        "query": query,
        "title": page.get("title", title),
        "text": trimmed_text,
        "text_length": len(full_text),
        "is_trimmed": len(full_text) > len(trimmed_text),
        "url": f"https://ko.wikipedia.org/wiki/{title.replace(' ', '_')}",
    }


TOOLS = [
    search_wikipedia,
]
