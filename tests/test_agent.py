import pytest
from agent import build_agent

@pytest.fixture
def agent():
    return build_agent()

def test_search_tool(agent):
    result = agent.invoke({
        "messages":[{"role":"user","content":"搜索一下LangChain是什么"}]
    })
    output = result["messages"][-1].content.lower()
    assert len(output)>10,"Agent回复太短,可能没有调用搜索工具"

def test_calculator_tool(agent):
    result = agent.invoke({
        "messages": [{"role": "user", "content": "计算 123 * 456 + 789"}]
    })
    output = result["messages"][-1].content
    assert "56877" in output,f"计算结果错误: {output}"

def test_multi_tool(agent):
    result = agent.invoke({
        "messages": [{"role": "user", "content": "搜索 Python 最新版本号，然后计算这个版本号的数字之和"}]
    })
    output = result["messages"][-1].content
    assert len(output) > 20, "多工具调用应该产生较长的回复"

if __name__=="__main__":
    pytest.main([__file__,"-v"])