import asyncio
from arq import cron
from src.infrastructure.config.loader import settings
from src.infrastructure.external.minio_storage import MinioStorageAdapter
from src.infrastructure.external.redis_stream_adapter import RedisStreamAdapter
from src.application.services.test_suite_runner import TestSuiteRunner
from src.presentation.schemas.automation import TestCase

# --- Task Definitions ---

async def run_test_suite_task(
    ctx, 
    job_id: str, 
    test_cases_raw: list, 
    base_url: str, 
    auth_data: dict = None,
    model_name: str = None
):
    """The background task executed by the arq worker."""
    # 1. Prepare dependencies
    storage = MinioStorageAdapter()
    messaging = RedisStreamAdapter()
    
    # Convert raw dicts back to Pydantic models
    test_cases = [TestCase(**tc) for tc in test_cases_raw]
    
    # 2. Initialize Runner
    runner = TestSuiteRunner(storage, messaging, job_id)
    
    # 3. Execute
    try:
        await runner.run_suite(test_cases, base_url, auth_data, model_name)
    except Exception as e:
        # Notify about failure
        await messaging.publish_event(job_id, {"type": "ERROR", "payload": {"message": str(e)}})
        raise e

# --- Worker Settings ---

class WorkerSettings:
    """Settings used by the arq worker process."""
    functions = [run_test_suite_task]
    redis_settings = settings.worker.redis_url # Uses url string directly
    
    # Arq expects redis_settings to be a RedisConfig instance or URL
    # We will use the URL from our config
    on_startup = None
    on_shutdown = None
    
    # Concurrency control
    max_jobs = settings.worker.concurrency
