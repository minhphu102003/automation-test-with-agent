import os
import shutil
import tempfile
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from config.pricing import DEFAULT_MODEL

# --- Services & Use Cases ---
from src.application.use_cases.get_metrics import GetHistoryUseCase
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.application.use_cases.run_excel import RunExcelAutomationUseCase
from src.application.use_cases.run_gpt_automation import RunGptAutomationUseCase
from src.application.use_cases.stream_job_updates import StreamJobUpdatesUseCase

# --- Schemas ---
from src.presentation.schemas.automation import (
    AutomationRunRequest, 
    AutomationRunResponse, 
    TestRunHistory,
    GPTImportRequest,
    JobResponse
)

# Centralized Dependency Injection
from src.infrastructure.di import providers


router = APIRouter(prefix="/automation", tags=["automation"])


@router.post("/run", response_model=AutomationRunResponse)
async def run_automation(
    request: AutomationRunRequest, 
    use_case: RunAutomationUseCase = Depends(providers.get_automation_use_case)
):
    run_id, _ = await use_case.execute(
        request.task, 
        request.model,
        profile_id=request.profile_id,
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
    use_case: RunExcelAutomationUseCase = Depends(providers.get_excel_use_case)
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
async def get_history(
    limit: int = 50, 
    use_case: GetHistoryUseCase = Depends(providers.get_history_use_case)
):
    return [TestRunHistory.from_domain(item) for item in use_case.execute(limit=limit)]

@router.post("/gpt-bridge/run", response_model=JobResponse)
async def run_gpt_automation(
    request: GPTImportRequest, 
    use_case: RunGptAutomationUseCase = Depends(providers.get_run_gpt_use_case)
):
    """Parses GPT text and enqueues a background job."""
    try:
        job_id = await use_case.execute(request.raw_text, base_url=request.base_url)
        return JobResponse(job_id=job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs/{job_id}/stream")
async def stream_job_updates(
    job_id: str,
    last_id: str = "0",
    use_case: StreamJobUpdatesUseCase = Depends(providers.get_stream_updates_use_case)
):
    """Streams job updates from Redis via SSE."""
    return StreamingResponse(
        use_case.execute(job_id, last_id), 
        media_type="text/event-stream"
    )
