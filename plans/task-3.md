# Task 3: The System Agent - Implementation Plan

## Objective
Add query_api tool to agent to query live backend API for system information.

## Implementation Plan

### 1. Tool Schema
Add to TOOLS array:
- name: "query_api"
- description: "Query the live backend API to get system data like item counts, framework info, analytics"
- parameters: method (GET/POST), path, body (optional)

### 2. Authentication
- Use LMS_API_KEY from .env.docker.secret
- Use AGENT_API_BASE_URL (default: http://localhost:42002)

### 3. Environment Variables
All config from env vars:
- LLM_API_KEY (from .env.agent.secret)
- LLM_API_BASE (from .env.agent.secret)
- LLM_MODEL (from .env.agent.secret)
- LMS_API_KEY (from .env.docker.secret)
- AGENT_API_BASE_URL (optional)

### 4. System Prompt Update
Teach LLM when to use:
- read_file/list_files → documentation
- query_api → live system data

### 5. Initial Benchmark Results
First run of run_eval.py: 0/10 passed
Main failures:
- Question 1: Missing branch protection info in wiki
- Question 2-3: API questions not working
- Question 4: Analytics endpoint not implemented

### 6. Iteration Strategy
1. Add branch protection info to wiki/github.md
2. Implement query_api with proper authentication
3. Test each question type
4. Pass all 10 questions
