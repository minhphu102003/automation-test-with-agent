from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field

from config.pricing import DEFAULT_MODEL
from src.domain.models.metrics import (
    MetricsSummary as DomainMetricsSummary,
    TestRunHistory as DomainTestRunHistory,
    TokenUsage as DomainTokenUsage,
)

class AutomationRunRequest(BaseModel):
    task: str = Field(..., example="Go to google.com and search for browser-use")
    model: str = Field(default=DEFAULT_MODEL, example=DEFAULT_MODEL)
    profile_id: Optional[str] = Field(None, example="main-staging")
    url: Optional[str] = Field(None, example="https://example.com/dashboard")
    cookies: Optional[Dict[str, str]] = Field(None, example={"session": "12345"})
    access_token: Optional[str] = Field(None, example="ey... (JWT)")
    token_key: Optional[str] = Field(None, example="access_token", description="The custom key to store the token in localStorage")
    width: Optional[int] = Field(None, example=1280, description="Browser viewport width")
    height: Optional[int] = Field(None, example=800, description="Browser viewport height")
    is_mobile: Optional[bool] = Field(False, description="Whether to emulate a mobile device")
    use_vision: Optional[bool] = Field(None, description="Whether to use vision-based processing. If None, it will be auto-detected.")
    max_steps: int = Field(default=5, description="The maximum number of steps the agent can take")
    wait_for_url: Optional[str] = Field(None, example="https://example.com/dashboard")
    wait_for_selector: Optional[str] = Field(None, example=".main-content")

class AutomationRunResponse(BaseModel):
    run_id: str
    status: str
    task: str
    model: str

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float

    @classmethod
    def from_domain(cls, usage: DomainTokenUsage) -> "TokenUsage":
        return cls(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost_usd=usage.estimated_cost_usd,
        )

class TestRunHistory(BaseModel):
    run_id: str
    task: str
    model: str
    status: str
    start_time: datetime
    duration_seconds: float
    usage: TokenUsage
    success: bool

    @classmethod
    def from_domain(cls, history: DomainTestRunHistory) -> "TestRunHistory":
        return cls(
            run_id=history.run_id,
            task=history.task,
            model=history.model,
            status=history.status,
            start_time=history.start_time,
            duration_seconds=history.duration_seconds,
            usage=TokenUsage.from_domain(history.usage),
            success=history.success,
        )

class MetricsSummary(BaseModel):
    total_runs: int
    success_rate: float
    total_cost_usd: float
    total_tokens: int
    avg_duration: float

    @classmethod
    def from_domain(cls, summary: DomainMetricsSummary) -> "MetricsSummary":
        return cls(
            total_runs=summary.total_runs,
            success_rate=summary.success_rate,
            total_cost_usd=summary.total_cost_usd,
            total_tokens=summary.total_tokens,
            avg_duration=summary.avg_duration,
        )

class TestCase(BaseModel):
    id: Optional[str] = Field(None, alias="Test Case ID")
    url: Optional[str] = Field(None, alias="URL")
    feature: Optional[str] = Field(None, alias="Module / Feature")
    scenario: Optional[str] = Field(None, alias="Test Scenario")
    title: Optional[str] = Field(None, alias="Test Case Title")
    description: Optional[str] = Field(None, alias="Description")
    preconditions: Optional[str] = Field(None, alias="Preconditions")
    data: Optional[str] = Field(None, alias="Test Data")
    steps: Optional[str] = Field(None, alias="Test Steps")
    expected: Optional[str] = Field(None, alias="Expected Result")
    actual: Optional[str] = Field(None, alias="Actual Result")
    status: Optional[str] = Field(None, alias="Status")
    comments: Optional[str] = Field(None, alias="Comments / Notes")

    class Config:
        populate_by_name = True

class GPTImportRequest(BaseModel):
    raw_text: str
    base_url: Optional[str] = "https://www.google.com"

class JobResponse(BaseModel):
    job_id: str
    status: str = "queued"
