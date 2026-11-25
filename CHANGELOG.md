# 更新日志 (CHANGELOG)

## [2026-11-25] — 新增 RAG 知识库问答能力

本次更新在原有「搜索 / 计算 / 天气」三工具基础上，接入本地技术文档知识库，
新增第四个工具 `rag_search`，实现「先检索、后作答、带来源」的检索增强生成，
降低模型凭记忆编造的幻觉问题。原有工具逻辑与整体结构未改动。

### 新增 (Added)

- **工具**：`tools/rag_tool.py` 新增 `rag_search` 检索工具，相似度 top-k 检索并把命中的文档片段连同 `【来源: xxx.md】` 标记注入 Agent。
- **语料库**：`knowledge_base/` 新增 24 篇 Markdown 语料，每篇 200–800 字，分三组——技术概念 8 篇、RAG 技术 8 篇、项目实战 8 篇。
- **建库脚本**：`rag/build_kb.py`，读取语料 → `RecursiveCharacterTextSplitter` 切分（chunk=500, overlap=80）→ SiliconFlow `BAAI/bge-m3` 向量化 → Chroma 持久化（实测 24 篇 → 30 个 chunk）。
- **测试**：`tests/test_rag.py`，覆盖「检索能返回结果」与「结果含来源、可溯源」两项断言（实测 2 passed）。
- **依赖**：`requirements.txt` 追加 `langchain-chroma`、`langchain-community`、`langchain-text-splitters`、`python-dotenv`。

### 变更 (Changed)

- `agent.py`：注册 `rag_search` 到工具列表；system prompt 追加第 4、5 条规则——知识性/框架类问题必须先检索；调用过检索后回答末尾必须单独列出 `来源：` 行并原样写出文件名。
- `main.py`：欢迎语由「搜索 / 计算 / 天气查询」改为「搜索 / 计算 / 天气查询 / 知识库检索」。
- `tools/__init__.py`：包导出列表加入 `rag_search`。
- `README.md`：追加「RAG 知识库问答（新增能力）」章节，说明链路、目录结构、重建命令与评测口径。
- `.gitignore`：新增 `chroma_db/`，忽略本地向量库构建产物。

### 修复 (Fixed)

- 端到端回答丢失来源标记的问题：检索工具已正确返回 `【来源: xxx.md】`，但模型生成最终答案时会把标记「消化」掉；通过强化 prompt 规则，回答末尾现已稳定输出 `来源：` 行。
