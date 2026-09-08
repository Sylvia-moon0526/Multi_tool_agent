# 🤖 多工具调用 Agent（Multi-Tool Agent）

> 基于 LangChain 构建的多工具调用智能体，能够自主决策并组合使用搜索引擎、计算器、天气 API 完成复杂任务。

---

## 📋 目录

- [项目简介](#-项目简介)
- [核心架构](#-核心架构)
- [目录结构](#-目录结构)
- [环境准备](#️-环境准备)
- [快速开始](#-快速开始)
- [工具详解](#-工具详解)
- [运行测试](#-运行测试)
- [设计决策](#-设计决策)
- [常见问题](#-常见问题)
- [面试要点](#-面试要点)
- [扩展方向](#-扩展方向)

---

## 📖 项目简介

这是一个 **ReAct（Reasoning + Acting）** 架构的 Agent 应用。它不像传统聊天机器人那样只能回答问题——它能 **自主选择工具**、**组合多个工具**、**处理复杂的多步骤任务**。

### 它能做什么？

| 用户输入 | Agent 行为 |
|:---------|:-----------|
| "上海今天天气怎么样？" | 调用天气工具 → 返回温度、湿度、风速 |
| "计算 123 × 456 + 789" | 调用计算器 → 返回 56877 |
| "LangChain 最新版本是多少？" | 调用搜索工具 → 返回搜索结果 |
| "搜一下 Python 最新版本，然后计算版本号数字之和" | **先搜索 → 再计算**（多步骤组合） |

### 技术栈

| 组件 | 技术选型 | 说明 |
|:-----|:---------|:-----|
| LLM | Qwen/Qwen3.5-9B | 通过 SiliconFlow API 调用 |
| Agent 框架 | LangChain `create_agent` | 底层基于 LangGraph ReAct |
| 搜索 | DuckDuckGo | 免费，无需 API Key |
| 天气 | OpenWeatherMap API | 免费额度 |
| 测试 | pytest | 单元测试 + 集成测试 |

---

## 🏗️ 核心架构

<details>
<summary><b>点击展开架构图</b></summary>

```
┌─────────────────────────────────────────────────────────┐
│                      用户输入                            │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent (create_agent)                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              ReAct 推理循环                        │   │
│  │                                                    │   │
│  │  Thought: 我需要搜索最新信息                       │   │
│  │  Action:  调用 search_tool                        │   │
│  │  Observation: [搜索结果...]                        │   │
│  │  Thought: 现在我有了信息，需要计算                  │   │
│  │  Action:  调用 calculator_tool                    │   │
│  │  Observation: 计算结果                             │   │
│  │  → 最终回复                                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  可用工具:                                              │
│  ├── 🔍 search_tool      (DuckDuckGo 搜索)             │
│  ├── 🧮 calculator_tool  (安全数学计算)                 │
│  └── 🌤️  get_weather     (OpenWeatherMap API)          │
│                                                         │
│  LLM: Qwen3.5-9B (SiliconFlow)                        │
└─────────────────────────────────────────────────────────┘
```

</details>

### ReAct 循环详解

Agent 的核心是一个 **Thought → Action → Observation** 的循环：

| 步骤 | 说明 |
|:-----|:-----|
| **1. Thought（思考）** | LLM 分析当前状态，决定下一步做什么 |
| **2. Action（行动）** | 选择并调用一个工具 |
| **3. Observation（观察）** | 获取工具返回结果 |
| **4. 循环判断** | 信息不够 → 继续下一轮；够了 → 生成最终回复 |

> 💡 这就是 Agent 和"普通 LLM 调用"的本质区别 —— **Agent 有行动能力**。

---

## 📁 目录结构

```
project1_multi_tool/
├── main.py                 # 入口文件，交互式命令行
├── agent.py                # Agent 构建逻辑（LLM + 工具注册）
├── tools/                  # 工具模块
│   ├── __init__.py         # 工具包初始化，统一导出
│   ├── search.py           # 🔍 搜索工具（DuckDuckGo）
│   ├── calculator.py       # 🧮 计算器工具（安全 eval）
│   └── weather.py          # 🌤️ 天气工具（OpenWeatherMap）
├── tests/
│   └── test_agent.py       # 单元测试（单工具 + 多工具组合）
├── requirements.txt        # 依赖清单
└── README.md               # 本文件
```

### 各文件职责

| 文件 | 职责 | 关键内容 |
|:-----|:-----|:---------|
| `main.py` | 用户交互入口 | 命令行循环、异常捕获 |
| `agent.py` | Agent 工厂函数 | LLM 初始化、工具注册、`create_agent` |
| `tools/search.py` | 搜索能力 | DuckDuckGo、`@tool` 装饰器 |
| `tools/calculator.py` | 计算能力 | 安全 `eval()`、白名单机制 |
| `tools/weather.py` | 天气能力 | REST API 调用、环境变量 |
| `tests/test_agent.py` | 质量保障 | pytest fixture、端到端测试 |

---

## ⚙️ 环境准备

### 系统要求

- Python >= 3.10
- pip 包管理器

### API Key 准备

| 服务 | 是否必须 | 获取方式 |
|:-----|:---------|:---------|
| SiliconFlow API Key | ✅ 必须 | [siliconflow.cn](https://siliconflow.cn) 注册后获取 |
| OpenWeatherMap API Key | ⚠️ 可选 | [openweathermap.org/api](https://openweathermap.org/api) 免费注册 |

> 💡 **没有 OpenWeatherMap Key？** 不影响其他功能，天气工具会返回提示信息。

---

## 🚀 快速开始

<details>
<summary><b>点击展开完整步骤</b></summary>

### 1. 克隆/进入项目目录

```bash
cd project1_multi_tool
```

### 2. 创建虚拟环境（推荐）

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

**Windows PowerShell:**
```powershell
$env:SILICONFLOW_API_KEY="sk-your-key-here"
$env:OPENWEATHER_API_KEY="your-weather-key"  # 可选
```

**Windows CMD:**
```cmd
set SILICONFLOW_API_KEY=sk-your-key-here
set OPENWEATHER_API_KEY=your-weather-key
```

**macOS / Linux:**
```bash
export SILICONFLOW_API_KEY="sk-your-key-here"
export OPENWEATHER_API_KEY="your-weather-key"  # 可选
```

### 5. 运行

```bash
python main.py
```

### 6. 开始交互

```
==================================================
🤖 多工具调用 Agent
支持: 搜索 / 计算 / 天气查询
输入 'quit' 退出
==================================================

你: 上海今天天气怎么样？

Agent: 📍 Shanghai 天气信息
       🌡️ 温度: 28°C (体感 30°C)
       🌤️ 天气: 多云
       💧 湿度: 65%
       💨 风速: 5 m/s

你: 计算 (123 + 456) * 789

Agent: (123 + 456) * 789 = 456567
```

</details>

---

## 🔧 工具详解

### 🔍 搜索工具 — `search_tool`

| 项目 | 说明 |
|:-----|:-----|
| 底层 | DuckDuckGo Search API |
| 优势 | 免费、无需注册、无请求量限制 |
| 输入 | 搜索关键词（`str`） |
| 输出 | 前 5 条搜索结果（标题 + 摘要 + 来源链接） |

```python
from tools.search import search_tool

result = search_tool.invoke("LangChain tutorial")
print(result)
```

### 🧮 计算器工具 — `calculator_tool`

| 项目 | 说明 |
|:-----|:-----|
| 底层 | Python `eval()` + 安全沙箱 |
| 安全机制 | 清空 `__builtins__`，白名单只允许安全数学函数 |
| 输入 | 数学表达式字符串（如 `"2 + 3 * 4"`） |
| 输出 | 计算结果（如 `"2 + 3 * 4 = 14"`） |

```python
from tools.calculator import calculator_tool

result = calculator_tool.invoke("math.sqrt(144) + 2 ** 10")
# 返回: "math.sqrt(144) + 2 ** 10 = 1036.0"
```

<details>
<summary><b>安全沙箱原理</b></summary>

```python
# 白名单：只允许安全的数学运算
allowed_names = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "pow": pow, "int": int, "float": float,
    "math": math,
}

# 清空 __builtins__ → 禁止 import/exec/open 等危险操作
result = eval(expression, {"__builtins__": {}}, allowed_names)
```

| 操作 | 是否允许 | 原因 |
|:-----|:---------|:-----|
| `2 + 3 * 4` | ✅ | 基本算术 |
| `math.sqrt(16)` | ✅ | 白名单内的 math 模块 |
| `__import__('os')` | ❌ | `__builtins__` 已清空 |
| `open('/etc/passwd')` | ❌ | `__builtins__` 已清空 |

</details>

### 🌤️ 天气工具 — `get_weather`

| 项目 | 说明 |
|:-----|:-----|
| 底层 | OpenWeatherMap REST API |
| 输入 | 城市名称（建议英文，如 `"Beijing"`） |
| 输出 | 温度、体感温度、天气状况、湿度、风速 |

```python
from tools.weather import get_weather

result = get_weather.invoke("Beijing")
print(result)
# 📍 Beijing 天气信息
# 🌡️ 温度: 25°C (体感 26°C)
# 🌤️ 天气: 晴
# 💧 湿度: 45%
# 💨 风速: 3 m/s
```

---

## 🧪 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行单个测试
pytest tests/test_agent.py::test_calculator_tool -v

# 显示详细输出
pytest tests/ -v -s
```

### 测试覆盖

| 测试用例 | 验证内容 |
|:---------|:---------|
| `test_search_tool` | Agent 能调用搜索工具并返回有效结果 |
| `test_calculator_tool` | Agent 能正确计算数学表达式（123×456+789 = 57057） |
| `test_multi_tool` | Agent 能组合多个工具完成多步骤任务 |

---

## 🎯 设计决策

### 为什么用 DuckDuckGo 而不是 Google/Bing？

- **零门槛** — 免费、无需 API Key、无需信用卡
- **快速验证** — 学习阶段先跑通流程，再替换生产级搜索
- **替换简单** — 只需修改 `tools/search.py` 一个文件

### 为什么计算器用 `eval()` 而不是 `sympy`？

- **面试加分** — 考察对 `eval()` 安全问题的理解
- **教学价值** — 白名单机制展示了"安全沙箱"的设计思路
- **够用** — 覆盖 95% 的日常数学计算需求

### 为什么用 `create_agent`（LangChain 新接口）？

- `create_agent` 是 LangChain 对旧版 `create_react_agent` 的统一入口
- 旧版 `langgraph.prebuilt.create_react_agent` 已标记为弃用，迁移到 `langchain.agents.create_agent`
- 底层仍然基于 LangGraph 的 ReAct 图执行，但 API 更简洁统一
- 体现对框架版本演进的了解

### 为什么 LLM 用 SiliconFlow 而不是直接调 OpenAI？

- **成本** — SiliconFlow 按量计费，学习阶段成本极低
- **速度** — 国内访问延迟低
- **灵活** — 可以随时切换模型（Qwen、GLM、DeepSeek 等）

---

## ❓ 常见问题

<details>
<summary><b>运行报错 KeyError: 'SILICONFLOW_API_KEY'</b></summary>

没有设置环境变量。按照 [快速开始](#-快速开始) 的第 4 步设置。

</details>

<details>
<summary><b>搜索工具返回空结果</b></summary>

DuckDuckGo 偶尔被墙。尝试：
1. 检查网络连接
2. 换个关键词
3. 等几分钟重试

</details>

<details>
<summary><b>天气工具提示未配置 API Key</b></summary>

正常现象。不需要天气功能可以忽略。需要的话去 [OpenWeatherMap](https://openweathermap.org/api) 免费注册获取 Key。

</details>

<details>
<summary><b>Pylance 显示"无法解析导入"</b></summary>

这是 VS Code 的静态检查问题，**不影响运行**。解决方法：

```bash
# 在项目根目录创建 .vscode/settings.json
mkdir -p .vscode
echo '{"python.analysis.extraPaths": ["."]}' > .vscode/settings.json
```

</details>

<details>
<summary><b>如何切换到其他 LLM？</b></summary>

修改 `agent.py` 中的 LLM 配置：

```python
# 切换到 DeepSeek-V3
llm = init_chat_model(
    model="deepseek-ai/DeepSeek-V3",
    model_provider="openai",
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url="https://api.siliconflow.cn/v1",
)
```

</details>

---

## 💼 面试要点

<details>
<summary><b>1. ReAct 架构</b></summary>

- **是什么**: Reasoning + Acting 的结合，LLM 既思考又行动
- **循环**: Thought → Action → Observation → 循环
- **优势**: 比纯 LLM 多了工具调用能力，比传统编程多了推理能力

</details>

<details>
<summary><b>2. Function Calling 机制</b></summary>

- LLM 不直接执行代码，而是输出 **结构化的工具调用请求**
- 框架解析请求，调用对应工具，把结果喂回 LLM
- 面试常问：LLM 怎么知道该调用哪个工具？
  - 答：**工具描述（docstring）+ 参数 schema**

</details>

<details>
<summary><b>3. Tool 设计原则</b></summary>

| 原则 | 说明 |
|:-----|:-----|
| 单一职责 | 一个工具只做一件事 |
| 清晰描述 | docstring 写清输入输出，是 LLM 选工具的依据 |
| 错误处理 | 工具不能崩，返回可读的错误信息 |
| 输入约束 | 类型检查、白名单，防止 LLM 传奇怪参数 |

</details>

<details>
<summary><b>4. 安全考虑</b></summary>

- `eval()` 的安全沙箱（白名单机制）
- API Key 的环境变量管理（不硬编码）
- `max_iterations` 防止 Agent 死循环

</details>

<details>
<summary><b>5. 可扩展性</b></summary>

新增工具只需 3 步：
1. 在 `tools/` 下新建 Python 文件
2. 用 `@tool` 装饰器定义工具函数
3. 在 `agent.py` 中注册到 `tools` 列表

工具之间解耦，可以独立测试。

</details>

---

## 🔮 扩展方向

如果你想继续完善这个项目：

### 功能扩展

- [ ] 添加**记忆模块**（ConversationBufferMemory）
- [ ] 添加**流式输出**（Streaming）
- [ ] 添加**更多工具**（翻译、股票查询、数据库查询）
- [ ] 支持**多轮对话**（保持上下文）

### 工程化

- [ ] 添加 **Streamlit Web UI**
- [ ] 添加 **日志记录**（logging 模块）
- [ ] 添加 **Docker 部署**
- [ ] 添加 **CI/CD**（GitHub Actions 自动测试）

### 进阶

- [ ] 实现**自定义 Agent Loop**（不用 `create_agent`，手写 ReAct 循环）
- [ ] 添加**工具调用轨迹记录**（用于调试和优化）
- [ ] 实现 **Human-in-the-loop**（关键决策需要人工确认）

---

## 📜 License

MIT

---

<p align="center">
  <strong>如果这个项目对你有帮助，请给个 ⭐ Star 支持！</strong>
</p>

---