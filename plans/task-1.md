# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider and Model
- **Provider**: Qwen Code API (OpenAI-compatible)
- **Model**: `qwen3-coder-plus`
- **Why**: 1000 free requests/day, works from Russia

## Agent Structure
The agent will:
1. Read configuration from `.env.agent.secret`
2. Parse question from command-line argument
3. Send request to LLM API
4. Output JSON with answer and empty tool_calls

## System Prompt
"You are a helpful assistant. Answer concisely."

## Output Format
{
  "answer": "The answer",
  "tool_calls": []
}

## Error Handling
- Missing config → error to stderr, exit 1
- API errors → error to stderr, exit 1
