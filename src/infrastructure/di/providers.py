from fastapi import Depends, Request
from src.domain.interfaces.metrics import IMetricsReader
from src.infrastructure.external.redis_stream_adapter import RedisStreamAdapter
from src.infrastructure.external.minio_storage import MinioStorageAdapter
from src.application.services.gpt_bridge import GPTBridgeService

# Use Cases
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.application.use_cases.run_excel import RunExcelAutomationUseCase
from src.application.use_cases.get_metrics import GetHistoryUseCase, GetMetricsSummaryUseCase
from src.application.use_cases.run_gpt_automation import RunGptAutomationUseCase
from src.application.use_cases.stream_job_updates import StreamJobUpdatesUseCase

# --- Service/Adapter Factories ---

def get_langfuse_reader(request: Request) -> IMetricsReader:
    return request.app.state.langfuse_reader

def get_messaging_service(request: Request) -> RedisStreamAdapter:
    return request.app.state.messaging

def get_storage_service(request: Request) -> MinioStorageAdapter:
    return request.app.state.storage

def get_gpt_bridge_service() -> GPTBridgeService:
    return GPTBridgeService()

# --- Use Case Factories ---

def get_automation_use_case() -> RunAutomationUseCase:
    return RunAutomationUseCase()

def get_excel_use_case() -> RunExcelAutomationUseCase:
    return RunExcelAutomationUseCase()

def get_history_use_case(
    reader: IMetricsReader = Depends(get_langfuse_reader)
) -> GetHistoryUseCase:
    return GetHistoryUseCase(reader)

def get_metrics_summary_use_case(
    reader: IMetricsReader = Depends(get_langfuse_reader)
) -> GetMetricsSummaryUseCase:
    return GetMetricsSummaryUseCase(reader)

def get_run_gpt_use_case(
    gpt_service: GPTBridgeService = Depends(get_gpt_bridge_service)
) -> RunGptAutomationUseCase:
    return RunGptAutomationUseCase(gpt_service)

def get_stream_updates_use_case(
    messaging: RedisStreamAdapter = Depends(get_messaging_service)
) -> StreamJobUpdatesUseCase:
    return StreamJobUpdatesUseCase(messaging)
