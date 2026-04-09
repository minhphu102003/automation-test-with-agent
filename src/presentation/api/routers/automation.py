from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from src.presentation.schemas.automation import AutomationRunRequest, AutomationRunResponse, TestRunHistory
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.application.use_cases.run_excel import RunExcelAutomationUseCase
from config.pricing import DEFAULT_MODEL
from src.application.use_cases.get_metrics import GetHistoryUseCase
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader
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

from src.application.use_cases.run_gpt_automation import RunGptAutomationUseCase
from src.infrastructure.external.redis_stream_adapter import RedisStreamAdapter
from src.presentation.schemas.automation import JobResponse
from src.infrastructure.config.loader import settings
import json
from fastapi.responses import StreamingResponse

# ... (rest of old logic)

@router.post("/gpt-bridge/run", response_model=JobResponse)
async def run_gpt_automation(
    request: GPTImportRequest, 
    use_case: RunGptAutomationUseCase = Depends(RunGptAutomationUseCase)
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
    adapter: RedisStreamAdapter = Depends(RedisStreamAdapter)
):
    """Streams job updates from Redis via SSE."""
    
    async def event_generator():
        current_id = last_id
        # Send initial message to establish connection
        yield f"id: 0\nevent: ping\ndata: {json.dumps({'message': 'connected'})}\n\n"
        
        while True:
            try:
                # Read from Redis stream
                events = await adapter.read_stream(job_id, last_id=current_id, timeout_ms=5000)
                
                for event in events:
                    current_id = event["id"]
                    payload = event["data"]
                    
                    # Yield in SSE format
                    yield f"id: {current_id}\nevent: message\ndata: {json.dumps(payload)}\n\n"
                    
                    # If job is finished or errored, we can stop streaming 
                    # (though client usually handles closing)
                    if payload.get("type") in ["RUNNER_FINISHED", "ERROR"]:
                        return

                # Heartbeat to keep connection alive
                if not events:
                    yield f": heartbeat\n\n"
                
                await asyncio.sleep(0.5)
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
                return

    return StreamingResponse(event_generator(), media_type="text/event-stream")
