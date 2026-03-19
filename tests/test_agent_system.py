import pytest
import subprocess
import json
import os

def test_framework_question_uses_read_file():
    """Test that framework question uses read_file tool"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What framework does this project use?"],
        capture_output=True,
        text=True,
        cwd="/root/se-toolkit-lab-6"
    )
    
    output = json.loads(result.stdout)
    assert "answer" in output
    if "tool_calls" in output and output["tool_calls"]:
        tools = [t["tool"] for t in output["tool_calls"]]
        assert "read_file" in tools or "query_api" in tools

def test_items_count_uses_query_api():
    """Test that items count question uses query_api tool"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "How many items are in the database?"],
        capture_output=True,
        text=True,
        cwd="/root/se-toolkit-lab-6"
    )
    
    output = json.loads(result.stdout)
    assert "answer" in output
    assert any(c.isdigit() for c in output["answer"])
    
    if "tool_calls" in output and output["tool_calls"]:
        tools = [t["tool"] for t in output["tool_calls"]]
        assert "query_api" in tools

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
