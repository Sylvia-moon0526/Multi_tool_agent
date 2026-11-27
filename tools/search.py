from langchain_core.tools import tool
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import re


def _query_tokens(query: str) -> list:
    tokens = set(re.findall(r"[a-zA-Z0-9]{2,}", query.lower()))
    tokens.update(re.findall(r"[\u4e00-\u9fff]{2,4}", query))
    return [t for t in tokens if len(t) >= 2]


def _is_relevant(result: dict, tokens: list) -> bool:
    if not tokens:
        return True
    text = (
        str(result.get("title", "")) + " "
        + str(result.get("body", "")) + " "
        + str(result.get("href", ""))
    ).lower()
    hits = sum(1 for t in tokens if t.lower() in text)
    return hits >= max(1, len(tokens) // 3)


def _bing_search(query: str, max_results: int, tokens: list = None) -> list:
    results = []
    for host in ["https://cn.bing.com/search", "https://www.bing.com/search"]:
        try:
            response = requests.get(
                host,
                params={"q": query, "setlang": "zh-hans", "cc": "CN"},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=10,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select("li.b_algo")[:max_results]:
                link = item.select_one("h2 a")
                snippet = item.select_one(".b_caption p")
                if not link:
                    continue
                results.append({
                    "title": link.get_text(" ", strip=True),
                    "body": snippet.get_text(" ", strip=True) if snippet else "无摘要",
                    "href": link.get("href", ""),
                })
            if results:
                break
        except Exception:
            continue
    if tokens:
        results = [r for r in results if _is_relevant(r, tokens)]
    return results[:max_results]


@tool
def search_tool(query:str)->str:
    """搜索互联网获取最新信息。输入搜索关键词,返回前5条搜索结果的摘要。"""
    tokens = _query_tokens(query)
    results = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception:
        pass

    if tokens:
        results = [r for r in results if _is_relevant(r, tokens)]

    if not results:
        results = _bing_search(query, 5, tokens)

    if not results:
        return "未找到相关结果，请尝试更换关键词。"

    output_parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "无标题")
        body = r.get("body", "无摘要")
        href = r.get("href", "")
        output_parts.append(f"[{i}] {title}\n{body}\n来源: {href}")
    return "\n\n".join(output_parts)
