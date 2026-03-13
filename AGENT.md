# Agent Documentation

## Overview
This agent calls the Qwen Code API via SSH tunnel and returns JSON responses.

## LLM Provider
- **Provider**: Qwen Code API
- **Model**: qwen3-coder-plus
- **Access**: Through SSH tunnel (localhost:42006)

## Configuration
File `.env.agent.secret` contains:
- `LLM_API_KEY=my-secret-qwen-key`
- `LLM_API_BASE=http://127.0.0.1:42006/v1`
- `LLM_MODEL=qwen3-coder-plus`

## SSH Tunnel Setup
Before running the agent, establish an SSH tunnel:
```bash
ssh -L 42006:127.0.0.1:42006 root@10.93.26.53
