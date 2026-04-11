from datetime import datetime, timezone
import unittest

from src.domain.models.metrics import MetricsSummary, TestRunHistory
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader


class _FakeTrace:
    def __init__(
        self,
        trace_id: str,
        metadata: dict,
        total_cost: float,
        timestamp: datetime,
    ) -> None:
        self.id = trace_id
        self.metadata = metadata
        self.total_cost = total_cost
        self.timestamp = timestamp


class _FakeTraceApi:
    def __init__(self, traces):
        self._traces = traces

    def list(self, limit: int, tags: list[str]):
        return type("Response", (), {"data": self._traces[:limit]})()


class _FakeLangfuseClient:
    def __init__(self, traces):
        self.api = type("Api", (), {"trace": _FakeTraceApi(traces)})()


class LangfuseReaderTest(unittest.TestCase):
    def test_get_history_maps_traces_to_domain_models(self) -> None:
        traces = [
            _FakeTrace(
                trace_id="trace-1",
                metadata={
                    "task": "Run checkout flow",
                    "model_name": "gpt-4o-mini",
                    "duration_seconds": 12.5,
                    "prompt_tokens": 100,
                    "completion_tokens": 40,
                    "total_tokens": 140,
                    "success": 1,
                },
                total_cost=0.0123,
                timestamp=datetime(2026, 4, 11, tzinfo=timezone.utc),
            )
        ]
        reader = LangfuseReader(client=_FakeLangfuseClient(traces))

        history = reader.get_history(limit=5)

        self.assertEqual(1, len(history))
        self.assertIsInstance(history[0], TestRunHistory)
        self.assertEqual("trace-1", history[0].run_id)
        self.assertEqual("Run checkout flow", history[0].task)
        self.assertEqual(140, history[0].usage.total_tokens)
        self.assertAlmostEqual(0.0123, history[0].usage.estimated_cost_usd)
        self.assertTrue(history[0].success)

    def test_get_summary_aggregates_trace_metadata(self) -> None:
        traces = [
            _FakeTrace(
                trace_id="trace-1",
                metadata={"success": 1, "duration_seconds": 10.0, "total_tokens": 100},
                total_cost=0.01,
                timestamp=datetime(2026, 4, 11, tzinfo=timezone.utc),
            ),
            _FakeTrace(
                trace_id="trace-2",
                metadata={"success": 0, "duration_seconds": 20.0, "total_tokens": 50},
                total_cost=0.02,
                timestamp=datetime(2026, 4, 11, tzinfo=timezone.utc),
            ),
        ]
        reader = LangfuseReader(client=_FakeLangfuseClient(traces))

        summary = reader.get_summary()

        self.assertIsInstance(summary, MetricsSummary)
        self.assertEqual(2, summary.total_runs)
        self.assertEqual(50.0, summary.success_rate)
        self.assertEqual(150, summary.total_tokens)
        self.assertAlmostEqual(0.03, summary.total_cost_usd)
        self.assertEqual(15.0, summary.avg_duration)
