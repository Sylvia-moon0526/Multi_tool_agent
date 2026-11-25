import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from tools.search import search_tool
from tools.calculator import calculator_tool
from tools.weather import get_weather
from tools.rag_tool import rag_search

def build_agent():
    llm = init_chat_model(
        model="Qwen/Qwen3.5-9B",
        model_provider="openai",
        model_kwargs={
            "temperature":0.3,
        },
        api_key=os.environ["SILICONFLOW_API_KEY"],
        base_url="https://api.siliconflow.cn/v1",
    )

    tools = [search_tool, calculator_tool, get_weather, rag_search]
    system_prompt = (
        "你是一个多工具调用智能体，可用工具：search_tool（搜索）、"
        "calculator_tool（数学计算，输入如 '2+3'、'math.sqrt(16)'）、"
        "get_weather（天气查询）、"
        "rag_search（检索本地技术知识库，回答技术概念、项目细节、框架用法等问题）。\n\n"
        "工作规则：\n"
        "1. 当任务包含多个连续步骤（例如『先搜索…再计算…』『查天气…然后计算…』）时，"
        "必须**分步依次调用不同工具**：先用前面的工具拿数据，再用 calculator_tool 对拿到的数据做计算，"
        "最后整合结果给出完整回答。不要只用其中一个工具就结束。\n"
        "2. 需要数值计算时（倍数、总和、增减后的结果等），一定要调用 calculator_tool。\n"
        "3. 直接回答前，用简洁清晰的中文总结结果，并记得把关键数值和单位写在回答里。\n"
        "4. 遇到知识性、技术概念、项目细节或框架用法类问题时，必须先用 rag_search 检索知识库，"
        "基于检索结果回答，不要仅凭记忆编造。\n"
        "5. 只要调用过 rag_search，回答末尾必须单独列出『来源：』一行，"
        "原样写出检索结果里每个【来源: xxx.md】中的文件名（如 react.md），不可省略、不可改写。"
    )
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    return agent

def run_agent(query:str):
    agent = build_agent()
    result = agent.invoke({"messages":[{"role":"user","content":query}]})
    final_message = result["messages"][-1]
    return final_message.content

if __name__ == "__main__":
    print("🤖 多工具调用 Agent 已启动")
    print("输入 'quit' 退出\n")
    
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("再见！")
            break
        if not user_input:
            continue
        
        try:
            response = run_agent(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\n❌ 出错: {str(e)}\n")