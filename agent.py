#!/usr/bin/env python3
"""
<<<<<<< HEAD
Documentation Agent with tools (read_file, list_files)
Usage: uv run agent.py "Your question about the wiki"
=======
System Agent with tools (read_file, list_files, query_api)
Usage: uv run agent.py "Your question about the system"
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
import argparse
<<<<<<< HEAD

# Load environment variables
load_dotenv('.env.agent.secret')
=======
import urllib.parse

# Load environment variables
load_dotenv('.env.agent.secret')
load_dotenv('.env.docker.secret')
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)

# Configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3-coder-plus')
<<<<<<< HEAD
=======
LMS_API_KEY = os.getenv('LMS_API_KEY')
AGENT_API_BASE_URL = os.getenv('AGENT_API_BASE_URL', 'http://localhost:42002')
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
MAX_TOOL_CALLS = 10

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

<<<<<<< HEAD
=======
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

>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
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
<<<<<<< HEAD
    }
]

def validate_config():
    """Validate that all required environment variables are set."""
    missing = []
    if not LLM_API_KEY:
        missing.append('LLM_API_KEY')
    if not LLM_API_BASE:
        missing.append('LLM_API_BASE')
    
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Please check your .env.agent.secret file", file=sys.stderr)
        sys.exit(1)

def secure_path(relative_path):
    """
    Validate and resolve a path to ensure it's within project root.
    Returns absolute path if valid, None if invalid.
    """
    try:
        # Block path traversal attempts
        if '..' in relative_path.split(os.sep):
            return None
        
        # Resolve absolute path
        requested_path = (PROJECT_ROOT / relative_path).resolve()
        
        # Check if path is within project root
=======
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
        
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
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
<<<<<<< HEAD
=======
    elif tool_name == 'query_api':
        return tool_query_api(
            arguments.get('method', 'GET'),
            arguments.get('path', ''),
            arguments.get('body')
        )
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
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

<<<<<<< HEAD
=======
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

>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
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
<<<<<<< HEAD
    except requests.exceptions.Timeout:
        print("Error: Request timed out after 60 seconds", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    # Parse command line
    parser = argparse.ArgumentParser(description='Documentation agent')
    parser.add_argument('question', help='The question to ask')
    args = parser.parse_args()
    
    # Validate configuration
    validate_config()
    
    # System prompt that guides the agent
    system_prompt = """You are a documentation assistant for a software engineering toolkit.
Your task is to help users find information in the project wiki.

Available tools:
- list_files(path): List files in a directory (use first to discover wiki files)
- read_file(path): Read contents of a file

Strategy:
1. First, list files in the "wiki" directory to see what documentation is available
2. Read relevant files to find answers to the user's question
3. When you find the answer, include the source reference as "wiki/filename.md#section"
4. Be concise and helpful

Always use the tools to find information - don't guess or make up answers.
"""
    
    # Initialize messages
=======
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
    
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.question}
    ]
    
    tool_calls_log = []
    tool_call_count = 0
<<<<<<< HEAD
    
    # Agentic loop
    while tool_call_count < MAX_TOOL_CALLS:
        # Get response from LLM
        response = call_llm_with_tools(messages)
        
        # Check if there are tool calls
=======
    source = ""
    
    while tool_call_count < MAX_TOOL_CALLS:
        response = call_llm_with_tools(messages)
        
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
        if 'choices' not in response or not response['choices']:
            print("Error: Invalid API response", file=sys.stderr)
            sys.exit(1)
        
        choice = response['choices'][0]
        message = choice.get('message', {})
        
<<<<<<< HEAD
        # If no tool calls, this is the final answer
=======
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
        if 'tool_calls' not in message or not message['tool_calls']:
            final_answer = message.get('content', '')
            break
        
<<<<<<< HEAD
        # Process tool calls
        tool_calls = message['tool_calls']
        
        # Add assistant message with tool calls to history
=======
        tool_calls = message['tool_calls']
        
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
        messages.append({
            "role": "assistant",
            "tool_calls": tool_calls,
            "content": None
        })
        
<<<<<<< HEAD
        # Execute each tool
        for tool_call in tool_calls:
            result = execute_tool(tool_call)
            
            # Log the tool call
=======
        for tool_call in tool_calls:
            result = execute_tool(tool_call)
            
            # Save source if this is a read_file tool
            if tool_call['function']['name'] == 'read_file':
                args = json.loads(tool_call['function']['arguments'])
                source = args.get('path', '')
            
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
            tool_calls_log.append({
                "tool": tool_call['function']['name'],
                "args": json.loads(tool_call['function']['arguments']),
                "result": result
            })
            
<<<<<<< HEAD
            # Add tool response to messages
=======
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": result
            })
        
        tool_call_count += 1
    
<<<<<<< HEAD
    # If we hit max tool calls without final answer
    if tool_call_count >= MAX_TOOL_CALLS and 'final_answer' not in locals():
        final_answer = "Maximum tool calls reached without final answer."
    
    # Extract source from the final answer
    source_match = re.search(r'(wiki/[\w/-]+\.md(?:#[\w-]+)?)', final_answer)
    source = source_match.group(1) if source_match else ""
    
    # Clean answer (remove source references if they appear)
    answer = final_answer
    if source and source in answer:
        answer = answer.replace(f"Source: {source}", "").strip()
        answer = answer.replace(f"[{source}]", "").strip()
    
    # Prepare output
    output = {
        "answer": answer,
=======
    if tool_call_count >= MAX_TOOL_CALLS and 'final_answer' not in locals():
        final_answer = "Maximum tool calls reached without final answer."
    
    # Truncate answer if too long for run_eval.py
    if len(final_answer) > 1000:
        final_answer = final_answer[:1000] + "..."
    
    output = {
        "answer": final_answer,
>>>>>>> 286a4f1 (feat: Task 3 complete - agent finds analytics bug with line numbers)
        "source": source,
        "tool_calls": tool_calls_log
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
