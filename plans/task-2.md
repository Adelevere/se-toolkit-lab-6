# Task 2: The Documentation Agent - Implementation Plan

## Tool Schemas
Two tools will be implemented:

### 1. read_file
Read contents of a file in the project
Parameters: path (string) - relative path from project root

### 2. list_files
List files and directories at a path
Parameters: path (string) - relative directory path from project root

## Security
- Block any path containing ".."
- Check that resolved path is within project root

## Agentic Loop
1. Send question + tool definitions to LLM
2. If LLM requests tool calls → execute them, add results to conversation
3. Repeat until LLM gives final answer or max 10 calls
4. Output JSON with answer, source, and tool_calls
