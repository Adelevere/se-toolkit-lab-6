# System Agent Documentation

## Task 3: The System Agent

### New Tool: query_api
The agent now has a `query_api` tool that can query the live backend API for real system information.

### Authentication
- **LMS_API_KEY**: Backend API key from `.env.docker.secret`
- **AGENT_API_BASE_URL**: Backend URL (defaults to http://localhost:42002)

### When to Use Which Tool
- **read_file**: Framework questions, documentation, source code
- **query_api**: Live system data (item counts, analytics)

### Common API Endpoints
- `GET /items/` - List all items
- `GET /items/count` - Number of items
- `GET /analytics/completion-rate?lab=XXX` - Completion rate

### Lessons Learned
1. The LLM needs clear instructions about tool usage
2. Framework information comes from source code, not API
3. Environment variables must be used for all configuration

### Final Benchmark Score
run_eval.py: 6/10 passed
