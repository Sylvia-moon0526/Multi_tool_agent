import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.rag_tool import rag_search


def test_rag_search_basic():
    result = rag_search.invoke("什么是 ReAct 模式？")
    assert result and "来源" in result


def test_rag_search_no_hallucination_source():
    result = rag_search.invoke("LangGraph 的优势是什么？")
    assert "来源" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
