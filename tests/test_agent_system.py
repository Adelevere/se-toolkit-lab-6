import pytest
import subprocess
import json
import os

def test_framework_question_uses_read_file():
    """Test that framework question uses read_file, not query_api"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What Python web framework does the backend use?"],
        capture_output=True,
        text=True,
        cwd="/root/se-toolkit-lab-6"
    )

    output = json.loads(result.stdout)
    assert "answer" in output

    # Check that read_file was used
    tool_calls = output.get("tool_calls", [])
    read_file_used = any(tool["tool"] == "read_file" for tool in tool_calls)
    query_api_used = any(tool["tool"] == "query_api" for tool in tool_calls)

    assert read_file_used, "Should use read_file for framework question"
    assert not query_api_used, "Should NOT use query_api for framework question"

def test_items_count_uses_query_api():
    """Test that items count question uses query_api"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "How many items are in the database?"],
        capture_output=True,
        text=True,
        cwd="/root/se-toolkit-lab-6"
    )

    output = json.loads(result.stdout)
    assert "answer" in output

    # Check that query_api was used
    tool_calls = output.get("tool_calls", [])
    query_api_used = any(tool["tool"] == "query_api" for tool in tool_calls)

    assert query_api_used, "Should use query_api for items count question"
    assert any(c.isdigit() for c in output["answer"]), "Answer should contain a number"

def test_analytics_bug_diagnosis():
    """Test that analytics bug diagnosis uses proper tool chain"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "Query the /analytics/completion-rate endpoint for a lab that has no data (e.g., lab-99). What error do you get, and what is the bug in the source code?"],
        capture_output=True,
        text=True,
        cwd="/root/se-toolkit-lab-6"
    )

    output = json.loads(result.stdout)
    assert "answer" in output

    tool_calls = output.get("tool_calls", [])
    tools_used = [tool["tool"] for tool in tool_calls]

    assert "query_api" in tools_used, "Should query the API first"
    assert "read_file" in tools_used, "Should read the source file"
