# Make telemetry a regular Python package
from .metrics import (
    track_node_latency,
    calculate_cost,
    record_llm_metrics,
    record_tool_metric,
    AGENT_RETRIES,
    AGENT_FAILURES
)
