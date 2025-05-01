from prometheus_client import Counter, Histogram, Gauge

# Create metrics once to avoid duplication
active_agent_count = Gauge(
    'active_agent_count',
    'Number of currently active agent processes'
)

http_requests_total = Counter(
    'http_requests_total', 
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'request_duration_seconds',
    'HTTP Request Duration in seconds',
    ['method', 'endpoint']
)

llm_request_count = Counter(
    'llm_request_count',
    'Number of LLM API requests',
    ['provider', 'status']
)

llm_response_time = Histogram(
    'llm_response_time_seconds',
    'LLM API response time in seconds',
    ['provider']
)

tool_execution_count = Counter(
    'tool_execution_count',
    'Number of tool executions',
    ['tool_name', 'status']
)

tool_execution_time = Histogram(
    'tool_execution_time_seconds',
    'Tool execution time in seconds',
    ['tool_name']
) 