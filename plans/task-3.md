# Task 3: The System Agent - Implementation Plan

## Objective
Add query_api tool to agent to query live backend API for system information.

## Implementation Plan

### 1. Tool Schema
Add query_api to TOOLS array:
- **name**: "query_api"
- **description**: "Query the live backend API to get system data"
- **parameters**: 
  - method: GET, POST, PUT, DELETE
  - path: API endpoint (e.g., /items/, /info/framework)
  - body: optional JSON

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
Teach LLM when to use each tool:
- **read_file**: documentation, source code, framework info
- **query_api**: live system data (items count, analytics)

### 5. Initial Benchmark Results
First run: 3/10 passed
Issues:
- Question 2: Framework question using query_api instead of read_file
- Question 4: Analytics endpoint error

### 6. Iteration Strategy
1. Fix framework question to use read_file
2. Add analytics endpoint handling
3. Pass all 10 questions
