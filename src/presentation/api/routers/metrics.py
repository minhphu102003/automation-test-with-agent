from fastapi import APIRouter, Depends
from src.presentation.schemas.automation import MetricsSummary
from src.application.use_cases.get_metrics import GetMetricsSummaryUseCase

from src.infrastructure.di import providers

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/summary", response_model=MetricsSummary)
async def get_summary(
    use_case: GetMetricsSummaryUseCase = Depends(providers.get_metrics_summary_use_case)
):
    return use_case.execute()
