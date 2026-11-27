import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge_base"
CHROMA_DIR = str(BASE_DIR / "chroma_db")


def build():
    if not KB_DIR.exists():
        raise RuntimeError(f"请先创建语料目录 {KB_DIR}")

    loader = DirectoryLoader(
        str(KB_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs = loader.load()
    if not docs:
        raise RuntimeError(f"{KB_DIR} 下没有找到 .md 文档")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", "。", "，", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        base_url="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        check_embedding_ctx_length=False,
    )

    Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    print(f"✅ 知识库构建完成：{len(docs)} 篇文档 -> {len(chunks)} 个 chunk")


if __name__ == "__main__":
    build()
