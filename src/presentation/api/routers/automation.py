from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from src.presentation.schemas.automation import AutomationRunRequest, AutomationRunResponse, TestRunHistory
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.application.use_cases.run_excel import RunExcelAutomationUseCase
from src.application.use_cases.get_metrics import GetHistoryUseCase
from src.infrastructure.monitoring.mlflow_reader import MLflowReader
from typing import List
import os
import shutil
import tempfile

router = APIRouter(prefix="/automation", tags=["automation"])

# Dependency Injection Setup
def get_mlflow_reader():
    return MLflowReader()

def get_automation_use_case():
    return RunAutomationUseCase()
    
def get_excel_use_case():
    return RunExcelAutomationUseCase()

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

@router.post("/run_excel")
async def run_excel_automation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    url: str = Form(...), 
    access_token: str = Form(""),
    use_case: RunExcelAutomationUseCase = Depends(get_excel_use_case)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        run_id, zip_path = await use_case.execute(tmp_path, url, access_token)
        os.remove(tmp_path)
        
        background_tasks.add_task(os.remove, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"automation_results_{run_id}.zip",
            media_type="application/zip"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[TestRunHistory])
async def get_history(limit: int = 50, reader: MLflowReader = Depends(get_mlflow_reader)):
    use_case = GetHistoryUseCase(reader)
    return use_case.execute(limit=limit)
