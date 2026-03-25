from fastapi import APIRouter, Depends
from src.presentation.schemas.automation import MetricsSummary
from src.application.use_cases.get_metrics import GetMetricsSummaryUseCase
from src.infrastructure.monitoring.mlflow_reader import MLflowReader

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Dependency Injection Setup
def get_mlflow_reader():
    return MLflowReader()

@router.get("/summary", response_model=MetricsSummary)
async def get_summary(reader: MLflowReader = Depends(get_mlflow_reader)):
    use_case = GetMetricsSummaryUseCase(reader)
    return use_case.execute()
