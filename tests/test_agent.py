import subprocess
import json
import sys

def test_agent():
    """Test that agent returns valid JSON with answer and tool_calls."""
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Agent failed with error: {result.stderr}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Invalid JSON output: {result.stdout}"
    
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be a list"
    assert output["answer"], "Answer should not be empty"
    
    print("✅ Test passed!")

if __name__ == "__main__":
    test_agent()
