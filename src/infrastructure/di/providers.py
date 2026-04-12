from typing import Any

from fastapi import Depends, Request
from src.application.use_cases.manage_profiles import ManageProfilesUseCase
from src.domain.interfaces.metrics import IMetricsReader
from src.domain.interfaces.auth_connector import IAuthConnector
from src.domain.interfaces.auth_profile_repository import IAuthProfileRepository
from src.application.services.gpt_bridge import GPTBridgeService

# --- Service/Adapter Factories ---

def get_langfuse_reader(request: Request) -> IMetricsReader:
    return request.app.state.langfuse_reader

def get_messaging_service(request: Request) -> Any:
    return request.app.state.messaging

def get_storage_service(request: Request) -> Any:
    return request.app.state.storage

def get_auth_profile_repository(request: Request) -> IAuthProfileRepository:
    return request.app.state.auth_profile_repository

def get_auth_connector(request: Request) -> IAuthConnector:
    return request.app.state.auth_connector

def get_gpt_bridge_service() -> GPTBridgeService:
    return GPTBridgeService()

# --- Use Case Factories ---

def get_manage_profiles_use_case(
    repository: IAuthProfileRepository = Depends(get_auth_profile_repository),
    connector: IAuthConnector = Depends(get_auth_connector),
) -> ManageProfilesUseCase:
    return ManageProfilesUseCase(repository, connector)

get_manage_auth_profiles_use_case = get_manage_profiles_use_case

def get_automation_use_case(
    profile_manager: ManageProfilesUseCase = Depends(get_manage_profiles_use_case),
) -> Any:
    from src.application.use_cases.run_automation import RunAutomationUseCase

    return RunAutomationUseCase(profile_manager=profile_manager)

def get_excel_use_case() -> Any:
    from src.application.use_cases.run_excel import RunExcelAutomationUseCase

    return RunExcelAutomationUseCase()

def get_history_use_case(
    reader: IMetricsReader = Depends(get_langfuse_reader)
) -> Any:
    from src.application.use_cases.get_metrics import GetHistoryUseCase

    return GetHistoryUseCase(reader)

def get_metrics_summary_use_case(
    reader: IMetricsReader = Depends(get_langfuse_reader)
) -> Any:
    from src.application.use_cases.get_metrics import GetMetricsSummaryUseCase

    return GetMetricsSummaryUseCase(reader)

def get_run_gpt_use_case(
    gpt_service: GPTBridgeService = Depends(get_gpt_bridge_service)
) -> Any:
    from src.application.use_cases.run_gpt_automation import RunGptAutomationUseCase

    return RunGptAutomationUseCase(gpt_service)

def get_stream_updates_use_case(
    messaging: Any = Depends(get_messaging_service)
) -> Any:
    from src.application.use_cases.stream_job_updates import StreamJobUpdatesUseCase

    return StreamJobUpdatesUseCase(messaging)
