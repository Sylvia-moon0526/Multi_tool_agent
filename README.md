# 🤖 多工具调用 Agent（Multi-Tool Agent）

<div align="center">

[Python](https://www.python.org/) · [LangChain](https://python.langchain.com/) · [LangGraph](https://langchain-ai.github.io/langgraph/) · [License: MIT](LICENSE)

</div>

> 基于 **LangChain + LangGraph** 构建的 ReAct（Reasoning + Acting）智能体。它能自主决策、按需组合异构工具，完成多步骤复杂任务——而不是像普通聊天机器人那样只能凭记忆回答。

---

## 📋 目录

- [它能做什么](#-它能做什么)
- [技术栈](#-技术栈)
- [核心架构](#-核心架构)
- [目录结构](#-目录结构)
- [环境准备](#-环境准备)
- [快速开始](#-快速开始)
- [工具详解](#-工具详解)
- [运行测试](#-运行测试)
- [设计决策](#-设计决策)
- [常见问题](#-常见问题)
- [面试要点](#-面试要点)
- [扩展方向](#-扩展方向)

---

## 🎯 它能做什么

| 用户输入 | Agent 行为 | 返回结果 |
| --- | --- | --- |
| "上海今天天气怎么样？" | 调用天气工具 | 温度、天气状况、风速（Open-Meteo 实时数据） |
| "计算 123 \* 456 + 789" | 调用计算器 | 56877 |
| "LangChain 最新版本是什么？" | 调用搜索工具 | 前 5 条搜索结果摘要 + 来源链接 |
| "搜一下 Python 最新版本，再计算版本号数字之和" | **先搜索 → 再计算**（多步骤组合） | 端到端组合结果 |

> 💡 这就是 Agent 与普通 LLM 调用的本质区别：**Agent 具备"行动能力"**——LLM 负责推理决策，框架负责执行工具并回喂结果。

---

## 🛠 技术栈

| 组件 | 技术选型 | 说明 |
| --- | --- | --- |
| LLM | `Qwen/Qwen3.5-9B` | 通过 SiliconFlow OpenAI 兼容接口调用（2026 年新模型，256K 上下文，支持 Tools） |
| Agent 框架 | LangChain `create_agent` | 底层基于 LangGraph 的 ReAct 图执行 |
| 搜索 | DuckDuckGo（`duckduckgo-search`） | 免费、无需 API Key |
| 计算 | Python `eval()` + 白名单沙箱 | 清空 `__builtins__`，只允许安全数学函数 |
| 天气 | **Open-Meteo API** | `geocoding-api.open-meteo.com` + `api.open-meteo.com`，**免费且无需任何 API Key** |
| 测试 | pytest | 单工具 + 多工具集成测试 |

---

## 🏗 核心架构

```
┌─────────────────────────────────────────────────────┐
│                      用户输入                        │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Agent（create_agent）                  │
│  ┌──────────────────────────────────────────────┐   │
│  │            ReAct 推理循环                     │   │
│  │  Thought: 我需要搜索最新信息                   │   │
│  │  Action:  调用 search_tool                    │   │
│  │  Observation: [搜索结果...]                   │   │
│  │  Thought: 现在我有了信息，需要计算             │   │
│  │  Action:  调用 calculator_tool               │    │
│  │  Observation: 计算结果                        │   │
│  │  → 生成最终回复                               │   │
│  └──────────────────────────────────────────────┘   │
│  可用工具:                                           │
│  ├── 🔍 search_tool      (DuckDuckGo)               │
│  ├── 🧮 calculator_tool  (安全 eval)                │
│  └── 🌤️  get_weather     (Open-Meteo)               │
│  LLM: Qwen/Qwen3.5-9B (SiliconFlow)                 │
└─────────────────────────────────────────────────────┘
```

### ReAct 循环详解

| 步骤 | 说明 |
| --- | --- |
| 1. Thought（思考） | LLM 分析当前状态，决定下一步做什么 |
| 2. Action（行动） | 选择并调用一个工具 |
| 3. Observation（观察） | 获取工具返回结果 |
| 4. 循环判断 | 信息不足 → 继续下一轮；信息充分 → 生成最终回复 |

---

## 📁 目录结构

```
Multi_tool_agent/
├── main.py                 # 入口文件，交互式命令行
├── agent.py                # Agent 构建逻辑（LLM + 工具注册）
├── tools/                  # 工具模块
│   ├── __init__.py         # 统一导出
│   ├── search.py           # 🔍 搜索工具（DuckDuckGo）
│   ├── calculator.py       # 🧮 计算器工具（安全 eval）
│   └── weather.py          # 🌤️ 天气工具（Open-Meteo）
├── tests/
│   └── test_agent.py       # 单元测试（单工具 + 多工具组合）
├── requirements.txt        # 依赖清单
└── README.md
```

| 文件 | 职责 | 关键内容 |
| --- | --- | --- |
| `main.py` | 用户交互入口 | 命令行循环、异常捕获 |
| `agent.py` | Agent 工厂函数 | `init_chat_model` 初始化、工具注册、`create_agent` |
| `tools/search.py` | 搜索能力 | DuckDuckGo、`@tool` 装饰器 |
| `tools/calculator.py` | 计算能力 | 安全 `eval()`、白名单机制 |
| `tools/weather.py` | 天气能力 | Open-Meteo REST API、中文城市别名、WMO 天气码映射 |
| `tests/test_agent.py` | 质量保障 | pytest fixture、端到端测试 |

---

## ⚙️ 环境准备

- **Python \>= 3.10**
- pip 包管理器
- 一个 **SiliconFlow API Key**（[siliconflow.cn](https://siliconflow.cn) 注册后获取）

> 💡 **天气工具无需任何 API Key**——使用 Open-Meteo 免费公开接口。搜索工具也无需 Key（DuckDuckGo）。全项目只需要一个 SiliconFlow Key。

---

## 🚀 快速开始

```bash
# 1. 克隆并进入项目（仓库根目录直接就是源码，没有子目录）
git clone https://github.com/Sylvia-moon0526/Multi_tool_agent.git
cd Multi_tool_agent

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（唯一必须的变量）
export SILICONFLOW_API_KEY="sk-your-key-here"
# Windows PowerShell: $env:SILICONFLOW_API_KEY="sk-your-key-here"
# Windows CMD:        set SILICONFLOW_API_KEY=sk-your-key-here

# 5. 运行
python main.py
```

交互示例：

```
==================================================
🤖 多工具调用 Agent
支持: 搜索 / 计算 / 天气查询
输入 'quit' 退出
==================================================

你: 计算 (123 + 456) * 789

Agent: (123 + 456) * 789 = 456831

你: 北京今天天气怎么样？

Agent: 📍 Beijing 天气信息
       🌡️ 温度: 25°C (体感约 25°C)
       🌤️ 天气: 晴
       💨 风速: 12 km/h
```

---

## 🔧 工具详解

### 🔍 搜索工具 — `search_tool`

| 项目 | 说明 |
| --- | --- |
| 底层 | DuckDuckGo Search API（`DDGS().text(query, max_results=5)`） |
| 优势 | 免费、无需注册 |
| 输入 | 搜索关键词（`str`） |
| 输出 | 前 5 条结果（标题 + 摘要 + 来源链接），无结果时返回提示语 |

### 🧮 计算器工具 — `calculator_tool`

| 项目 | 说明 |
| --- | --- |
| 底层 | Python `eval()` + 安全沙箱 |
| 安全机制 | 清空 `__builtins__`，白名单只允许 `abs/round/min/max/sum/pow/int/float/math` |
| 输入 | 数学表达式（如 `"math.sqrt(144) + 2 ** 10"`） |
| 输出 | `"表达式 = 结果"`，异常时返回可读错误信息而非抛出 |

```python
# 安全沙箱核心实现（tools/calculator.py）
allowed_names = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "pow": pow, "int": int, "float": float, "math": math,
}
result = eval(expression, {"__builtins__": {}}, allowed_names)
```

| 操作 | 是否允许 | 原因 |
| --- | --- | --- |
| `2 + 3 * 4` | ✅ | 基本算术 |
| `math.sqrt(16)` | ✅ | 白名单内的 math 模块 |
| `__import__('os')` | ❌ | `__builtins__` 已清空 |

> ⚠️ **安全说明（面试加分点）**：清空 `__builtins__` + 白名单能挡住绝大多数直接调用，但理论上仍可能被 `().__class__.__mro__[1].__subclasses__()` 这类属性链逃逸。生产环境应改用 `ast.literal_eval`、`asteval` 库或独立沙箱进程。**此处保留 **`eval`** 是为了展示安全沙箱的设计思路**。

### 🌤️ 天气工具 — `get_weather`

| 项目 | 说明 |
| --- | --- |
| 底层 | Open-Meteo Geocoding API + Forecast API（免费、无需 Key） |
| 输入 | 城市名（中文或英文均可，内置 18 个中文城市别名映射） |
| 输出 | 温度、天气状况（WMO 天气码转中文）、风速（km/h） |
| 容错 | 超时、找不到城市、网络异常均返回可读信息，不会崩溃 |

```python
from tools.weather import get_weather
result = get_weather.invoke("Beijing")
# 📍 Beijing 天气信息
# 🌡️ 温度: 25°C (体感约 25°C)
# 🌤️ 天气: 晴
# 💨 风速: 12 km/h
```

---

## 🧪 运行测试

```bash
pytest tests/ -v
# 运行单个测试
pytest tests/test_agent.py::test_calculator_tool -v
```

| 测试用例 | 验证内容 |
| --- | --- |
| `test_search_tool` | Agent 能调用搜索工具并返回有效结果 |
| `test_calculator_tool` | Agent 正确计算 `123 * 456 + 789 = 56877` |
| `test_multi_tool` | Agent 能组合多个工具完成多步骤任务 |

---

## 🎯 设计决策

**为什么用 DuckDuckGo 而不是 Google/Bing？**
零门槛（免费、无需 Key）、快速验证流程、替换成本低（只改 `tools/search.py` 一个文件）。

**为什么计算器用 **`eval()`** 而不是 **`sympy`**？**
展示对 `eval()` 安全问题的理解（白名单机制），覆盖绝大多数日常计算需求。

**为什么用 **`create_agent`**（LangChain 新接口）？**
`create_agent` 是 LangChain 对旧版 `create_react_agent` 的统一入口，底层仍基于 LangGraph 的 ReAct 图执行，API 更简洁，体现对框架版本演进的了解。

**为什么用 SiliconFlow？**
按量计费成本低、国内访问延迟低、可随时切换模型（Qwen / GLM / DeepSeek 等）。

**为什么天气用 Open-Meteo？**
完全免费、无需注册 API Key，让项目真正做到"只需一个 Key 即可全功能运行"。

---

## ❓ 常见问题

`KeyError: 'SILICONFLOW_API_KEY'`
未设置环境变量，按快速开始第 4 步设置。

**搜索工具返回空结果**
DuckDuckGo 偶尔不稳定：检查网络、换关键词、稍后重试。

**天气提示"找不到城市"**
确认城市名拼写；中文城市在内置别名表中（北京/上海/广州/深圳等 18 个），其他可用英文。

**Pylance 显示"无法解析导入"**
VS Code 静态检查问题，不影响运行。在项目根创建 `.vscode/settings.json`：

```json
{"python.analysis.extraPaths": ["."]}
```

**如何切换 LLM？**
修改 `agent.py` 中的 `init_chat_model` 参数：

```python
llm = init_chat_model(
    model="deepseek-ai/DeepSeek-V3",
    model_provider="openai",
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url="https://api.siliconflow.cn/v1",
)
```

---



## 🔮 扩展方向

- 功能：记忆模块、流式输出、更多工具（翻译/数据库查询）、多轮对话
- 工程：Streamlit Web UI、logging、**MCP 协议暴露工具**、FastAPI 服务化、Docker 部署、GitHub Actions CI
- 进阶：手写 ReAct 循环（不用 `create_agent`）、工具调用轨迹记录、Human-in-the-loop

---

## 📜 License

MIT
