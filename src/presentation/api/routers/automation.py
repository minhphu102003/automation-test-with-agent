from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from src.presentation.schemas.automation import AutomationRunRequest, AutomationRunResponse, TestRunHistory
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.application.use_cases.run_excel import RunExcelAutomationUseCase
from config.pricing import DEFAULT_MODEL
from src.application.use_cases.get_metrics import GetHistoryUseCase
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader
from typing import List
import os
import shutil
import tempfile
import pandas as pd
import io
from fastapi.responses import Response
from src.application.services.gpt_bridge import GPTBridgeService
from src.presentation.schemas.automation import GPTImportRequest

router = APIRouter(prefix="/automation", tags=["automation"])

# Dependency Injection Setup
def get_langfuse_reader():
    return LangfuseReader()

def get_automation_use_case():
    return RunAutomationUseCase()
    
def get_excel_use_case():
    return RunExcelAutomationUseCase()

def get_gpt_bridge_service():
    return GPTBridgeService()

@router.post("/run", response_model=AutomationRunResponse)
async def run_automation(request: AutomationRunRequest, use_case: RunAutomationUseCase = Depends(get_automation_use_case)):
    run_id, _ = await use_case.execute(
        request.task, 
        request.model,
        url=request.url,
        cookies=request.cookies,
        access_token=request.access_token,
        token_key=request.token_key,
        width=request.width,
        height=request.height,
        is_mobile=request.is_mobile,
        use_vision=request.use_vision,
        max_steps=request.max_steps,
        wait_for_url=request.wait_for_url,
        wait_for_selector=request.wait_for_selector
    )
    return AutomationRunResponse(
        run_id=run_id,
        status="completed",
        task=request.task,
        model=request.model
    )

@router.post("/run_excel")
async def run_excel_automation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    url: str = Form(...), 
    access_token: str = Form(""),
    cookies: Optional[str] = Form(None),
    model: str = Form(DEFAULT_MODEL),
    use_vision: Optional[bool] = Form(None),
    max_steps: int = Form(5),
    wait_for_url: Optional[str] = Form(None),
    wait_for_selector: Optional[str] = Form(None),
    use_case: RunExcelAutomationUseCase = Depends(get_excel_use_case)
):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        run_id, zip_path = await use_case.execute(
            tmp_path, 
            url, 
            access_token, 
            cookies=cookies,
            model_name=model,
            use_vision=use_vision,
            max_steps=max_steps,
            wait_for_url=wait_for_url,
            wait_for_selector=wait_for_selector
        )
        background_tasks.add_task(os.remove, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"automation_results_{run_id}.zip",
            media_type="application/zip"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.get("/history", response_model=List[TestRunHistory])
async def get_history(limit: int = 50, reader: LangfuseReader = Depends(get_langfuse_reader)):
    use_case = GetHistoryUseCase(reader)
    return use_case.execute(limit=limit)

# GPT Bridge Endpoints
@router.post("/gpt-bridge/prepare")
async def prepare_gpt_prompt(
    file: UploadFile = File(...),
    service: GPTBridgeService = Depends(get_gpt_bridge_service)
):
    """Takes a raw Excel file and returns a prompt for GPT Web."""
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        prompt = service.prepare_prompt(df)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Excel: {str(e)}")

@router.post("/gpt-bridge/convert")
async def convert_gpt_to_excel(
    request: GPTImportRequest,
    service: GPTBridgeService = Depends(get_gpt_bridge_service)
):
    """Takes GPT output (text) and returns a downloadable Excel file."""
    try:
        test_cases = service.parse_gpt_output(request.raw_text)
        if not test_cases:
            raise HTTPException(status_code=400, detail="Could not parse any test cases from the provided text.")
        
        excel_data = service.export_to_excel(test_cases)
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=optimized_test_cases.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting GPT output: {str(e)}")
