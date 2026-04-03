from fastapi import APIRouter, Depends
from src.presentation.schemas.automation import MetricsSummary
from src.application.use_cases.get_metrics import GetMetricsSummaryUseCase
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Dependency Injection Setup
def get_langfuse_reader():
    return LangfuseReader()

@router.get("/summary", response_model=MetricsSummary)
async def get_summary(reader: LangfuseReader = Depends(get_langfuse_reader)):
    use_case = GetMetricsSummaryUseCase(reader)
    return use_case.execute()
