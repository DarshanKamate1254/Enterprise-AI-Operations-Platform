import os
import sys
import unittest
from unittest.mock import MagicMock

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from monitoring.telemetry import (
    calculate_cost,
    record_llm_metrics,
    record_tool_metric,
    track_node_latency
)
from prometheus_client import REGISTRY


class TestTelemetryInstrumentation(unittest.TestCase):

    # 1. COST CALCULATION TESTS
    def test_cost_calculation_formulas(self):
        """Verify the financial pricing logic returns precise USD estimations."""
        # GPT-4o-mini pricing: prompt $0.15/1M, completion $0.60/1M
        mini_cost = calculate_cost(1000, 2000, "gpt-4o-mini")
        expected_mini = (1000 * 0.15 / 1_000_000) + (2000 * 0.60 / 1_000_000)
        self.assertAlmostEqual(mini_cost, expected_mini, places=9)

        # GPT-4o pricing: prompt $5.00/1M, completion $15.00/1M
        standard_cost = calculate_cost(1000, 2000, "gpt-4o")
        expected_standard = (1000 * 5.00 / 1_000_000) + (2000 * 15.00 / 1_000_000)
        self.assertAlmostEqual(standard_cost, expected_standard, places=9)

    # 2. LLM TOKENS & COST METRICS LOGGING
    def test_record_llm_metrics_updates_counters(self):
        """Verify LLM usage properties increment prompt, completion, and cost counters."""
        agent = "sql"
        
        # Capture current counter values before invoking metrics recorder
        init_prompts = REGISTRY.get_sample_value("llm_tokens_total", {"agent": agent, "type": "prompt"}) or 0.0
        init_completions = REGISTRY.get_sample_value("llm_tokens_total", {"agent": agent, "type": "completion"}) or 0.0
        init_cost = REGISTRY.get_sample_value("llm_cost_usd_total", {"agent": agent}) or 0.0
        
        # Custom Response object to bypass MagicMock guards
        class DummyResponse:
            def __init__(self):
                self.response_metadata = {
                    "token_usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50
                    }
                }
        mock_response = DummyResponse()
        
        record_llm_metrics(agent, mock_response, "gpt-4o-mini")
        
        # Verify increments
        new_prompts = REGISTRY.get_sample_value("llm_tokens_total", {"agent": agent, "type": "prompt"}) or 0.0
        new_completions = REGISTRY.get_sample_value("llm_tokens_total", {"agent": agent, "type": "completion"}) or 0.0
        new_cost = REGISTRY.get_sample_value("llm_cost_usd_total", {"agent": agent}) or 0.0
        
        self.assertEqual(new_prompts, init_prompts + 100)
        self.assertEqual(new_completions, init_completions + 50)
        
        expected_cost_diff = calculate_cost(100, 50, "gpt-4o-mini")
        self.assertAlmostEqual(new_cost - init_cost, expected_cost_diff, places=9)

    # 3. TOOL INVOCATION METRIC LOGGING
    def test_record_tool_metric(self):
        """Verify tool calls increment the tool metrics counter."""
        tool = "sql_tool"
        init_val = REGISTRY.get_sample_value("tool_invocations_total", {"tool": tool}) or 0.0
        
        record_tool_metric(tool)
        
        new_val = REGISTRY.get_sample_value("tool_invocations_total", {"tool": tool}) or 0.0
        self.assertEqual(new_val, init_val + 1)

    # 4. LATENCY TRACKING METRICS
    def test_track_node_latency(self):
        """Verify track_node_latency context manager registers operational spans."""
        node = "router"
        init_count = REGISTRY.get_sample_value("agent_node_latency_seconds_count", {"node": node}) or 0.0
        
        with track_node_latency(node):
            # Simple busy waiting simulation
            for _ in range(1000):
                pass
                
        new_count = REGISTRY.get_sample_value("agent_node_latency_seconds_count", {"node": node}) or 0.0
        self.assertEqual(new_count, init_count + 1)


if __name__ == "__main__":
    unittest.main()
