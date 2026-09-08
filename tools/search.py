from langchain_core.tools import tool
from duckduckgo_search import DDGS

@tool
def search_tool(query:str)->str:
    """搜索互联网获取最新信息。输入搜索关键词,返回前5条搜索结果的摘要。"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query,max_results=5))
        if not results:
            return "未找到相关结果，请尝试更换关键词。"
        output_parts = []
        for i,r in enumerate(results,1):
            title = r.get("title", "无标题")
            body = r.get("body", "无摘要")
            href = r.get("href", "")
            output_parts.append(f"[{i}] {title}\n{body}\n来源: {href}")

            return "\n\n".join(output_parts)
    except Exception as e:
        return f"搜索失败: {str(e)}"
            