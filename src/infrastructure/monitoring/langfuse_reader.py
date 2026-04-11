from datetime import datetime, timezone
from typing import List

from langfuse import Langfuse

from src.domain.interfaces.metrics import IMetricsReader
from src.domain.models.metrics import MetricsSummary, TestRunHistory, TokenUsage


class LangfuseReader(IMetricsReader):
    def __init__(
        self,
        experiment_name: str = "Browser Automation Tests",
        client: Langfuse | None = None,
    ):
        self.experiment_name = experiment_name
        self.langfuse = client or Langfuse()
        
    def get_history(self, limit: int = 50) -> List[TestRunHistory]:
        try:
            traces_response = self.langfuse.api.trace.list(limit=limit, tags=[self.experiment_name])
            traces = getattr(traces_response, 'data', [])
        except Exception as e:
            print(f"Error fetching traces from Langfuse: {e}")
            return []

        history = []
        for t in traces:
            metadata = getattr(t, 'metadata', {}) or {}
            
            usage = TokenUsage(
                prompt_tokens=metadata.get("prompt_tokens", 0),
                completion_tokens=metadata.get("completion_tokens", 0),
                total_tokens=metadata.get("total_tokens", 0),
                estimated_cost_usd=float(getattr(t, 'total_cost', 0.0) or 0.0)
            )

            success = metadata.get("success", 1)
            duration = metadata.get("duration_seconds", 0.0)
            
            # Note: t.timestamp comes back as datetime from SDK
            start_time = getattr(t, 'timestamp', datetime.now(timezone.utc))

            history.append(TestRunHistory(
                run_id=str(t.id),
                task=metadata.get("task", "N/A"),
                model=metadata.get("model_name", "N/A"),
                status="COMPLETED",
                start_time=start_time,
                duration_seconds=float(duration),
                usage=usage,
                success=bool(success)
            ))
            
        return history

    def get_summary(self) -> MetricsSummary:
        try:
            traces_response = self.langfuse.api.trace.list(limit=100, tags=[self.experiment_name])
            traces = getattr(traces_response, 'data', [])
        except Exception as e:
            print(f"Error fetching traces from Langfuse: {e}")
            traces = []

        if not traces:
            return MetricsSummary(
                total_runs=0,
                success_rate=0.0,
                total_cost_usd=0.0,
                total_tokens=0,
                avg_duration=0.0,
            )
            
        total_runs = len(traces)
        
        success_count = 0
        total_duration = 0.0
        total_tokens = 0
        
        for t in traces:
            metadata = getattr(t, 'metadata', {}) or {}
            success_count += metadata.get("success", 1)
            total_duration += metadata.get("duration_seconds", 0.0)
            total_tokens += metadata.get("total_tokens", 0)

        success_rate = (success_count / total_runs) * 100 if total_runs > 0 else 0
        total_cost = sum(float(getattr(t, 'total_cost', 0.0) or 0.0) for t in traces)
        avg_duration = total_duration / total_runs if total_runs > 0 else 0.0
        
        return MetricsSummary(
            total_runs=total_runs,
            success_rate=success_rate,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            avg_duration=avg_duration,
        )
