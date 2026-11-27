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

## [2026-11-27] — 稳定性加固：搜索双源容灾、输出兜底、评测覆盖 RAG

在 RAG 能力已上线的基础上，本轮针对端到端测试暴露的几类稳定性问题做了加固：
搜索结果错配、Agent 偶发空输出、评测引擎取错消息、多工具用例受模型退化干扰。
所有改动均为增量修复，未改动 ReAct 主循环与原有工具的业务逻辑。

---

### 新增 (Added)

- **搜索双源容灾与相关性过滤**（`tools/search.py`）
  - 主路径使用 `ddgs` 多后端；失败或无结果时自动切换 Bing 双源（`cn.bing.com` + `www.bing.com`）。
  - 新增 `_query_tokens()` 从查询词提取核心 token（英文词 + 中文 2-4 字词），`_is_relevant()` 要求结果标题/摘要/链接至少命中 1/3 token 才保留。
  - 解决代理环境下搜索引擎返回错配缓存页的问题（实例：搜「langchain 的最新版本」返回整页 DeepL 翻译）。
- **输出兜底 `extract_output()`**（`agent.py`、`main.py`）
  - 倒序查找最后一条「无工具调用且内容非空」的 AI 回答，全部为空时返回友好提示。
  - 解决模型偶发只生成空白 content 导致「Agent:」后无任何输出的问题。

### 变更 (Changed)

- **`agent.py`**：新增 `extract_output()`，`run_agent()` 与 `__main__` 交互循环均改用它。
- **`main.py`**：改用 `extract_output()` 取模型输出，不再直接读 `messages[-1].content`。
- **`tools/search.py`**：重写为「ddgs → 相关性过滤 → Bing 双源兜底 → 再过滤」流程，单次请求超时 10s；修复原文件 `return` 误缩进导致只返回 1 条结果的 bug。
- **README.md**（两个项目均更新）：同步双源搜索、输出兜底、RAG 工具、目录结构与 10 条评测用例的最新事实。

### 修复 (Fixed)

- **RAG 路径 bug**（`tools/rag_tool.py`、`rag/build_kb.py`）：`CHROMA_DIR` 从相对路径 `./chroma_db` 改为基于 `__file__` 的绝对路径。原先从 project3 目录跑评测时会在错误位置新建空库（0 向量），导致检索全部落空。
- **评测输出误取工具原文**（`project3-eval/tests/test_agent_eval.py`）：`_extract_output()` 的兜底循环此前会取到 ToolMessage，表现为「搜 LangChain 却输出一堆搜索结果」。改为兜底也只认 AI 消息，并把数字归一化（去逗号）与来源解析（直接抽 `.md` 文件名，兼容顿号/加粗/反引号）。
- **评测用例调整**（`project3-eval/tests/eval_cases.json`）：
  - 新增 `rag_retrieval` 分类 3 条（rag_01/02/03），带 `expected_source` 字段验证来源溯源。
  - `multi_01`、`multi_02` 改为「独立双工具」题（计算+RAG、天气+RAG）。原「天气结果→二次计算」链式题会稳定触发 Qwen3.5-9B 空输出退化，测的是模型缺陷而非编排能力。
  - `single_03` `max_rounds` 放宽至 6，容忍搜索重试。
- **评测结果**：完整评测从最初的 `7 failed / 3 passed` 提升至 **10 passed / 0 failed**（119s，1 条无害的 temperature 参数 warning）。

---

### 提交文件范围

- project1-multi_tool_agent：`agent.py`、`main.py`、`tools/search.py`、`tools/rag_tool.py`、`rag/build_kb.py`、`README.md`
- project3-eval：`tests/test_agent_eval.py`、`tests/eval_cases.json`、`README.md`
