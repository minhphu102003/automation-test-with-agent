from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


@dataclass(frozen=True, slots=True)
class TestRunHistory:
    run_id: str
    task: str
    model: str
    status: str
    start_time: datetime
    duration_seconds: float
    usage: TokenUsage
    success: bool


@dataclass(frozen=True, slots=True)
class MetricsSummary:
    total_runs: int
    success_rate: float
    total_cost_usd: float
    total_tokens: int
    avg_duration: float
