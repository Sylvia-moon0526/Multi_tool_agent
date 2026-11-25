import os
from pathlib import Path
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = "./chroma_db"
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        embeddings = OpenAIEmbeddings(
            model="BAAI/bge-m3",
            base_url="https://api.siliconflow.cn/v1",
            api_key=os.getenv("SILICONFLOW_API_KEY"),
            check_embedding_ctx_length=False,
        )
        db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
        _retriever = db.as_retriever(search_kwargs={"k": 3})
    return _retriever


@tool
def rag_search(query: str) -> str:
    """检索本地技术知识库，返回与问题最相关的文档片段及来源。
    当用户提问涉及：项目架构、Agent/LLM/RAG 等技术概念、LangChain/LangGraph 用法、
    API 配置等需要查阅资料的问题时，必须调用此工具，不要凭记忆编造答案。"""
    try:
        docs = _get_retriever().invoke(query)
        if not docs:
            return "知识库中未找到相关内容。"
        parts = []
        for d in docs:
            src = Path(d.metadata.get("source", "unknown")).name
            parts.append(f"【来源: {src}】\n{d.page_content}")
        return "\n\n---\n\n".join(parts)
    except Exception as e:
        return f"知识库检索失败: {e}"
