from fastapi import APIRouter, Depends, HTTPException
from src.presentation.schemas.automation import AutomationRunRequest, AutomationRunResponse, TestRunHistory
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.application.use_cases.get_metrics import GetHistoryUseCase
from src.infrastructure.monitoring.mlflow_reader import MLflowReader
from typing import List

router = APIRouter(prefix="/automation", tags=["automation"])

# Dependency Injection Setup
def get_mlflow_reader():
    return MLflowReader()

def get_automation_use_case():
    return RunAutomationUseCase()

@router.post("/run", response_model=AutomationRunResponse)
async def run_automation(request: AutomationRunRequest, use_case: RunAutomationUseCase = Depends(get_automation_use_case)):
    try:
        run_id, _ = await use_case.execute(request.task, request.model)
        return AutomationRunResponse(
            run_id=run_id,
            status="completed",
            task=request.task,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[TestRunHistory])
async def get_history(limit: int = 50, reader: MLflowReader = Depends(get_mlflow_reader)):
    use_case = GetHistoryUseCase(reader)
    return use_case.execute(limit=limit)
