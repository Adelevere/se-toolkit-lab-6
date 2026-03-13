#!/usr/bin/env python3
"""
Documentation Agent with tools (read_file, list_files)
Usage: uv run agent.py "Your question about the wiki"
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv('.env.agent.secret')

# Configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3-coder-plus')
MAX_TOOL_CALLS = 10

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

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
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.question}
    ]
    
    tool_calls_log = []
    tool_call_count = 0
    
    # Agentic loop
    while tool_call_count < MAX_TOOL_CALLS:
        # Get response from LLM
        response = call_llm_with_tools(messages)
        
        # Check if there are tool calls
        if 'choices' not in response or not response['choices']:
            print("Error: Invalid API response", file=sys.stderr)
            sys.exit(1)
        
        choice = response['choices'][0]
        message = choice.get('message', {})
        
        # If no tool calls, this is the final answer
        if 'tool_calls' not in message or not message['tool_calls']:
            final_answer = message.get('content', '')
            break
        
        # Process tool calls
        tool_calls = message['tool_calls']
        
        # Add assistant message with tool calls to history
        messages.append({
            "role": "assistant",
            "tool_calls": tool_calls,
            "content": None
        })
        
        # Execute each tool
        for tool_call in tool_calls:
            result = execute_tool(tool_call)
            
            # Log the tool call
            tool_calls_log.append({
                "tool": tool_call['function']['name'],
                "args": json.loads(tool_call['function']['arguments']),
                "result": result
            })
            
            # Add tool response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": result
            })
        
        tool_call_count += 1
    
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
        "source": source,
        "tool_calls": tool_calls_log
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
