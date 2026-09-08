import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from tools.search import search_tool
from tools.calculator import calculator_tool
from tools.weather import get_weather

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

    tools = [search_tool, calculator_tool, get_weather]
    agent = create_agent(
        model=llm,
        tools=tools,
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