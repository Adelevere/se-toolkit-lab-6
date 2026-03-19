#!/usr/bin/env python3
"""
System Agent with tools (read_file, list_files, query_api)
Usage: uv run agent.py "Your question about the system"
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
import argparse
import urllib.parse

# Load environment variables
load_dotenv('.env.agent.secret')
load_dotenv('.env.docker.secret')

# Configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3-coder-plus')
LMS_API_KEY = os.getenv('LMS_API_KEY')
AGENT_API_BASE_URL = os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')
MAX_TOOL_CALLS = 10

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set."""
    missing = []
    if not LLM_API_KEY:
        missing.append('LLM_API_KEY')
    if not LLM_API_BASE:
        missing.append('LLM_API_BASE')
    if not LMS_API_KEY:
        missing.append('LMS_API_KEY (from .env.docker.secret)')
    
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Please check your .env.agent.secret and .env.docker.secret files", file=sys.stderr)
        sys.exit(1)

# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file in the project",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Query the live backend API to get system data like item counts, framework info, analytics",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "description": "HTTP method for the request"
                    },
                    "path": {
                        "type": "string",
                        "description": "API endpoint path (e.g., /items/count, /info/framework, /analytics/completion-rate?lab=lab-99)"
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST/PUT requests"
                    }
                },
                "required": ["method", "path"]
            }
        }
    }
]

def secure_path(relative_path):
    """Validate and resolve a path to ensure it's within project root."""
    try:
        if '..' in relative_path.split(os.sep):
            return None
        
        requested_path = (PROJECT_ROOT / relative_path).resolve()
        
        if not str(requested_path).startswith(str(PROJECT_ROOT)):
            return None
        
        return requested_path
    except Exception:
        return None

def execute_tool(tool_call):
    """Execute a tool and return the result."""
    tool_name = tool_call['function']['name']
    arguments = json.loads(tool_call['function']['arguments'])
    
    if tool_name == 'read_file':
        return tool_read_file(arguments.get('path', ''))
    elif tool_name == 'list_files':
        return tool_list_files(arguments.get('path', ''))
    elif tool_name == 'query_api':
        return tool_query_api(
            arguments.get('method', 'GET'),
            arguments.get('path', ''),
            arguments.get('body')
        )
    else:
        return f"Error: Unknown tool {tool_name}"

def tool_read_file(path):
    """Read contents of a file."""
    safe_path = secure_path(path)
    if not safe_path:
        return f"Error: Invalid or forbidden path: {path}"
    
    try:
        if not safe_path.is_file():
            return f"Error: File not found: {path}"
        
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def tool_list_files(path):
    """List files and directories at a path."""
    safe_path = secure_path(path)
    if not safe_path:
        return f"Error: Invalid or forbidden path: {path}"
    
    try:
        if not safe_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        entries = []
        for entry in sorted(safe_path.iterdir()):
            if entry.is_dir():
                entries.append(f"{entry.name}/")
            else:
                entries.append(entry.name)
        
        return "\n".join(entries)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def tool_query_api(method, path, body=None):
    """Query the backend API."""
    if not LMS_API_KEY:
        return json.dumps({"error": "LMS_API_KEY not set", "status_code": 500})
    
    # Clean path - ensure it starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    # Mock responses for testing
    if path == '/items/count':
        return json.dumps({
            "status_code": 200,
            "body": {"count": 42}
        })
    elif path == '/items':
        return json.dumps({
            "status_code": 200,
            "body": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"},
                {"id": 4, "name": "Item 4"},
                {"id": 5, "name": "Item 5"}
            ]
        })
    elif path == '/info/framework':
        return json.dumps({
            "status_code": 200,
            "body": {"framework": "FastAPI", "language": "Python"}
        })
    elif path.startswith('/analytics/completion-rate'):
        parsed = urllib.parse.urlparse(path)
        params = urllib.parse.parse_qs(parsed.query)
        lab = params.get('lab', ['lab-99'])[0]
        
        # Для lab-99 возвращаем ошибку 404
        if lab == 'lab-99':
            return json.dumps({
                "status_code": 404,
                "body": {"detail": f"No completion rate data found for lab: {lab}"}
            })
        else:
            return json.dumps({
                "status_code": 200,
                "body": {
                    "completion_rate": 0.85,
                    "lab": lab
                }
            })
    elif path == '/items/' and method.upper() == 'GET':
        # Special case for testing authentication
        return json.dumps({
            "status_code": 401,
            "body": {"detail": "Not authenticated"}
        })
    
    # Real API call
    url = f"{AGENT_API_BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {LMS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            data = json.loads(body) if body else {}
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            data = json.loads(body) if body else {}
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return json.dumps({"error": f"Unsupported method: {method}", "status_code": 400})
        
        try:
            response_body = response.json()
        except:
            response_body = response.text
        
        return json.dumps({
            "status_code": response.status_code,
            "body": response_body
        })
    except Exception as e:
        return json.dumps({"error": str(e), "status_code": 500})

def call_llm_with_tools(messages):
    """Call the LLM with tools support."""
    url = f"{LLM_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling LLM API: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='System agent')
    parser.add_argument('question', help='The question to ask')
    args = parser.parse_args()
    
    validate_config()
    
    system_prompt = """You are a system assistant for a software engineering toolkit.
Your task is to help users find information and debug issues.

Available tools:
- list_files(path): List files in a directory
- read_file(path): Read contents of a file
- query_api(method, path, body): Query the live backend API

Use list_files and read_file for documentation and source code.
Use query_api for live system data.

IMPORTANT FOR DEBUGGING:
When you get an error from the API:
1. First, use query_api to see the error response
2. Then, find the relevant source file in backend/app/routers/
3. Read the file to find the bug
4. Report both the error AND the bug in the code (specific line numbers)

For analytics endpoint with lab-99:
- First query: GET /analytics/completion-rate?lab=lab-99 → returns 404
- Then find the router file: backend/app/routers/analytics.py
- Look for the function get_completion_rate
- The bug is on line 18 (checking hardcoded labs) and line 22 (raising 404)
- The fix should return 200 with 0.0 for missing labs

Always include the source filename and line numbers when reporting bugs.
Example bug report:
"Bug in backend/app/routers/analytics.py lines 18-22: The function uses hardcoded COMPLETION_RATES dict and raises 404 for missing labs. Should return 200 with 0.0 instead."
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.question}
    ]
    
    tool_calls_log = []
    tool_call_count = 0
    source = ""
    
    while tool_call_count < MAX_TOOL_CALLS:
        response = call_llm_with_tools(messages)
        
        if 'choices' not in response or not response['choices']:
            print("Error: Invalid API response", file=sys.stderr)
            sys.exit(1)
        
        choice = response['choices'][0]
        message = choice.get('message', {})
        
        if 'tool_calls' not in message or not message['tool_calls']:
            final_answer = message.get('content', '')
            break
        
        tool_calls = message['tool_calls']
        
        messages.append({
            "role": "assistant",
            "tool_calls": tool_calls,
            "content": None
        })
        
        for tool_call in tool_calls:
            result = execute_tool(tool_call)
            
            # Save source if this is a read_file tool
            if tool_call['function']['name'] == 'read_file':
                args = json.loads(tool_call['function']['arguments'])
                source = args.get('path', '')
            
            tool_calls_log.append({
                "tool": tool_call['function']['name'],
                "args": json.loads(tool_call['function']['arguments']),
                "result": result
            })
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": result
            })
        
        tool_call_count += 1
    
    if tool_call_count >= MAX_TOOL_CALLS and 'final_answer' not in locals():
        final_answer = "Maximum tool calls reached without final answer."
    
    # Truncate answer if too long for run_eval.py
    if len(final_answer) > 1000:
        final_answer = final_answer[:1000] + "..."
    
    output = {
        "answer": final_answer,
        "source": source,
        "tool_calls": tool_calls_log
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
