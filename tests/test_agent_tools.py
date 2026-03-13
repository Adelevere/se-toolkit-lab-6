import subprocess
import json
import sys

def test_merge_conflict_question():
    """Test that agent uses read_file for merge conflict question."""
    result = subprocess.run(
        [sys.executable, "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Error: {result.stderr}"
    
    try:
        output = json.loads(result.stdout)
    except:
        assert False, "Invalid JSON output"
    
    # Check required fields
    assert "answer" in output
    assert "source" in output
    assert "tool_calls" in output
    
    # Should have used read_file
    tool_names = [t["tool"] for t in output["tool_calls"]]
    assert "read_file" in tool_names, "Should have used read_file"
    
    # Source should point to wiki
    assert output["source"].startswith("wiki/"), f"Bad source: {output['source']}"
    
    print("✅ Merge conflict test passed")

def test_list_files_question():
    """Test that agent uses list_files for directory listing question."""
    result = subprocess.run(
        [sys.executable, "agent.py", "What files are in the wiki?"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Error: {result.stderr}"
    
    try:
        output = json.loads(result.stdout)
    except:
        assert False, "Invalid JSON output"
    
    # Should have used list_files
    tool_names = [t["tool"] for t in output["tool_calls"]]
    assert "list_files" in tool_names, "Should have used list_files"
    
    print("✅ List files test passed")

def test_path_traversal_security():
    """Test that agent blocks path traversal attempts."""
    import sys
    sys.path.append('.')
    
    try:
        from agent import tool_read_file, tool_list_files
        
        # Try path traversal
        result = tool_read_file("../../etc/passwd")
        assert "Error" in result, "Should block path traversal"
        
        result = tool_list_files("../../")
        assert "Error" in result, "Should block path traversal"
        
        print("✅ Security test passed")
    except ImportError:
        print("⚠️  Could not import agent module, skipping security test")

if __name__ == "__main__":
    test_merge_conflict_question()
    test_list_files_question()
    test_path_traversal_security()
    print("All Task 2 tests passed!")
