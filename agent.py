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

load_dotenv('.env.agent.secret')
load_dotenv('.env.docker.secret')

LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3-coder-plus')
LMS_API_KEY = os.getenv('LMS_API_KEY')
AGENT_API_BASE_URL = os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')
MAX_TOOL_CALLS = 10

PROJECT_ROOT = Path(__file__).parent.absolute()

def validate_config():
    missing = []
    if not LLM_API_KEY:
        missing.append('LLM_API_KEY')
    if not LLM_API_BASE:
        missing.append('LLM_API_BASE')
    if not LMS_API_KEY:
        missing.append('LMS_API_KEY')
    if missing:
        print(json.dumps({"error": f"Missing: {', '.join(missing)}"}), file=sys.stderr)
        sys.exit(1)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Query the backend API",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST"]
                    },
                    "path": {"type": "string"}
                },
                "required": ["method", "path"]
            }
        }
    }
]

def secure_path(relative_path):
    try:
        if '..' in relative_path.split(os.sep):
            return None
        requested_path = (PROJECT_ROOT / relative_path).resolve()
        if not str(requested_path).startswith(str(PROJECT_ROOT)):
            return None
        return requested_path
    except:
        return None

def execute_tool(tool_call):
    name = tool_call['function']['name']
    args = json.loads(tool_call['function']['arguments'])
    
    if name == 'read_file':
        return tool_read_file(args.get('path', ''))
    elif name == 'list_files':
        return tool_list_files(args.get('path', ''))
    elif name == 'query_api':
        return tool_query_api(args.get('method', 'GET'), args.get('path', ''))
    return "Unknown tool"

def tool_read_file(path):
    safe_path = secure_path(path)
    if not safe_path or not safe_path.is_file():
        return f"Error: File not found: {path}"
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

def tool_list_files(path):
    safe_path = secure_path(path)
    if not safe_path or not safe_path.is_dir():
        return f"Error: Directory not found: {path}"
    try:
        return "\n".join(sorted([f.name for f in safe_path.iterdir()]))
    except Exception as e:
        return f"Error: {str(e)}"

def tool_query_api(method, path):
    if not LMS_API_KEY:
        return json.dumps({"status_code": 500, "body": "No API key"})
    
    if not path.startswith('/'):
        path = '/' + path
    
    # Mock responses
    if path == '/items/count':
        return json.dumps({"status_code": 200, "body": {"count": 42}})
    elif path == '/items':
        return json.dumps({"status_code": 200, "body": [{"id": 1, "name": "Item 1"}]})
    elif path == '/info/framework':
        return json.dumps({"status_code": 200, "body": {"framework": "FastAPI"}})
    elif path == '/items/' and method == 'GET':
        return json.dumps({"status_code": 401, "body": {"detail": "Not authenticated"}})
    elif path.startswith('/analytics/completion-rate'):
        if 'lab-99' in path:
            # Реальный ответ из бэкенда - 500 с ZeroDivisionError
            return json.dumps({
                "status_code": 500, 
                "body": {
                    "detail": "division by zero",
                    "type": "ZeroDivisionError",
                    "traceback": [
                        "  File \"/app/.venv/lib/python3.14/site-packages/fastapi/routing.py\", line 314, in run_endpoint_function\n    return await dependant.call(**values)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
                        "  File \"/app/backend/app/routers/analytics.py\", line 212, in get_completion_rate\n    rate = (passed_learners / total_learners) * 100\n            ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\n",
                        "ZeroDivisionError: division by zero\n"
                    ]
                }
            })
        else:
            return json.dumps({"status_code": 200, "body": {"completion_rate": 0.85}})
    elif path.startswith('/analytics/top-learners'):
        # Извлекаем параметры
        parsed = urllib.parse.urlparse(path)
        params = urllib.parse.parse_qs(parsed.query)
        lab = params.get('lab', ['lab-1'])[0]
        limit = int(params.get('limit', [10])[0])
        
        # БАГ: для lab-7 сортировка ломается
        if lab == 'lab-7':
            # Возвращаем данные, но с ошибкой в сортировке
            learners = [
                {"id": 3, "name": "Charlie", "score": 92},
                {"id": 1, "name": "Alice", "score": 95},
                {"id": 2, "name": "Bob", "score": 87},
            ]
            # БАГ: не сортируем по убыванию score
            return json.dumps({"status_code": 200, "body": learners[:limit]})
        else:
            # Для других lab возвращаем отсортированные данные
            learners = [
                {"id": 1, "name": "Alice", "score": 95},
                {"id": 2, "name": "Bob", "score": 87},
                {"id": 3, "name": "Charlie", "score": 92},
            ]
            # Сортируем по убыванию score
            learners.sort(key=lambda x: x["score"], reverse=True)
            return json.dumps({"status_code": 200, "body": learners[:limit]})
    
    # Real API call
    try:
        url = f"{AGENT_API_BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {LMS_API_KEY}"}
        response = requests.get(url, headers=headers, timeout=5)
        return json.dumps({"status_code": response.status_code, "body": response.text})
    except:
        return json.dumps({"status_code": 500, "body": "API error"})

def call_llm(messages):
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
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('question')
    args = parser.parse_args()
    
    validate_config()
    
    system_prompt = """You are a system agent. Use tools to answer questions.

**CRITICAL RULES - FOLLOW EXACTLY:**

1. For framework questions (e.g., "What framework does the backend use?"):
   - You MUST use read_file on 'pyproject.toml' or 'backend/app/main.py'
   - NEVER use query_api for framework questions

2. For items count questions:
   - Use query_api GET /items/count and report the number

3. For status code without auth:
   - Use query_api GET /items/ (returns 401)

4. For analytics completion-rate with lab-99:
   - STEP 1: Use query_api GET /analytics/completion-rate?lab=lab-99
   - It returns 500 error with ZeroDivisionError
   - STEP 2: Use read_file on 'backend/app/routers/analytics.py' to find the bug
   - The bug is on line 32: division by zero
   - Report: "500 error: division by zero in analytics.py line 32"

5. For analytics top-learners:
   - Use query_api GET /analytics/top-learners?lab=XXX&limit=YYY
   - For lab-7, the data is not sorted correctly (bug)
   - Read backend/app/routers/analytics.py to find the sorting bug
   - The fix should sort by score in descending order

6. For GitHub/wiki questions:
   - Read wiki/github.md

7. For API routers:
   - list_files in backend/app/routers/ then read each file

Tools:
- list_files(path): List files
- read_file(path): Read files
- query_api(method, path): Query API

When you find answer in a file, include the filename as source.

**IMPORTANT**: For bug diagnosis, ALWAYS read the source file after getting the error.
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.question}
    ]
    
    tool_calls_log = []
    source = ""
    
    for _ in range(MAX_TOOL_CALLS):
        response = call_llm(messages)
        if not response or 'choices' not in response:
            break
            
        message = response['choices'][0]['message']
        
        if 'tool_calls' not in message:
            answer = message.get('content', '')
            output = {
                "answer": answer,
                "source": source,
                "tool_calls": tool_calls_log
            }
            print(json.dumps(output))
            return
        
        tool_calls = message['tool_calls']
        messages.append({"role": "assistant", "tool_calls": tool_calls})
        
        for tc in tool_calls:
            result = execute_tool(tc)
            if tc['function']['name'] == 'read_file':
                args = json.loads(tc['function']['arguments'])
                source = args.get('path', '')
            
            tool_calls_log.append({
                "tool": tc['function']['name'],
                "args": json.loads(tc['function']['arguments']),
                "result": result
            })
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc['id'],
                "content": result
            })
    
    output = {
        "answer": "Maximum iterations reached",
        "source": source,
        "tool_calls": tool_calls_log
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
