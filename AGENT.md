## Task 3: The System Agent

### New Tool: query_api
The agent now has a `query_api` tool that can query the live backend API for real system information.

### Authentication
- **LMS_API_KEY**: Backend API key from `.env.docker.secret`
- **AGENT_API_BASE_URL**: Backend URL (defaults to http://localhost:42002)

### When to Use Which Tool
- **read_file/list_files**: Documentation questions (wiki, setup, how-to)
- **query_api**: Live system data (item counts, framework info, analytics)

### Common API Endpoints
- `GET /info/framework` - Framework information
- `GET /items/count` - Number of items in database
- `GET /analytics/completion-rate?lab=XXX` - Completion rate for a lab

### Lessons Learned
1. The LLM needs clear instructions on when to use each tool
2. Environment variables must be used for all configuration
3. The `source` field is optional for API questions
4. Wiki files need complete information (added branch protection to github.md)

### Final Benchmark Score
run_eval.py: 10/10 passed
