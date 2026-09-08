from agent import build_agent


def main():
    print("=" * 50)
    print("🤖 多工具调用 Agent")
    print("支持: 搜索 / 计算 / 天气查询")
    print("输入 'quit' 退出")
    print("=" * 50)
    print()
    
    agent = build_agent()
    
    while True:
        user_input = input("你: ").strip()
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("再见！")
            break
        
        if not user_input:
            continue
        
        try:
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            final_message = result["messages"][-1]
            print(f"\nAgent: {final_message.content}\n")
            
        except Exception as e:
            print(f"\n❌ 出错: {str(e)}\n")


if __name__ == "__main__":
    main()
