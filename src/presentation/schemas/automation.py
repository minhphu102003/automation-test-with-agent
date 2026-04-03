from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class AutomationRunRequest(BaseModel):
    task: str = Field(..., example="Go to google.com and search for browser-use")
    model: str = Field(default="gpt-4o-mini", example="gpt-4o-mini")
    url: Optional[str] = Field(None, example="https://example.com/login")
    cookies: Optional[Dict[str, str]] = Field(None, example={"session": "12345"})
    access_token: Optional[str] = Field(None, example="ey... (JWT)")

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

class TestRunHistory(BaseModel):
    run_id: str
    task: str
    model: str
    status: str
    start_time: datetime
    duration_seconds: float
    usage: TokenUsage
    success: bool

class MetricsSummary(BaseModel):
    total_runs: int
    success_rate: float
    total_cost_usd: float
    total_tokens: int
    avg_duration: float
