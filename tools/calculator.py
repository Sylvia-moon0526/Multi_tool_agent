from langchain_core.tools import tool
import math

@tool
def calculator_tool(expression:str)->str:
    """计算数学表达式。输入数学表达式（如'2+3+4'、'math.sqrt(16)',返回计算结果。"""
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
        "math": math,
    }
    try:
        result = eval(expression,{"__builtins__":{}},allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败: {str(e)}，请检查表达式是否正确"