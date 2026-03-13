#!/usr/bin/env python3
"""
Agent that calls an LLM and returns a JSON response.
Usage: uv run agent.py "Your question here"
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.agent.secret')

# Configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_BASE = os.getenv('LLM_API_BASE')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3-coder-plus')

def main():
    # Get question from command line
    if len(sys.argv) < 2:
        print("Error: Please provide a question", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Check config
    if not LLM_API_KEY or not LLM_API_BASE:
        print("Error: Missing LLM_API_KEY or LLM_API_BASE in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    # Prepare API request
    url = f"{LLM_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer concisely."},
            {"role": "user", "content": question}
        ]
    }
    
    try:
        # Call API
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        answer = result['choices'][0]['message']['content']
        
        # Output JSON
        output = {
            "answer": answer.strip(),
            "tool_calls": []
        }
        print(json.dumps(output))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
