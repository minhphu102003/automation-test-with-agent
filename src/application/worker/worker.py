import asyncio
from arq import cron
from arq.connections import RedisSettings
from src.infrastructure.config.loader import settings
from src.infrastructure.external.minio_storage import MinioStorageAdapter
from src.infrastructure.external.redis_stream_adapter import RedisStreamAdapter
from src.application.services.test_suite_runner import TestSuiteRunner
from src.presentation.schemas.automation import TestCase

# --- Task Definitions ---

async def on_startup(ctx):
    """Initializes shared dependencies when the worker starts."""
    print("--- [Worker] Initializing dependencies ---")
    storage = MinioStorageAdapter()
    messaging = RedisStreamAdapter()
    runner = TestSuiteRunner(storage, messaging)
    
    ctx['storage'] = storage
    ctx['messaging'] = messaging
    ctx['runner'] = runner

async def on_shutdown(ctx):
    """Cleanup dependencies (e.g., closing Redis connections)."""
    print("--- [Worker] Cleaning up dependencies ---")
    storage = ctx.get('storage')
    messaging = ctx.get('messaging')
    
    if storage:
        await storage.close()
    if messaging:
        await messaging.close()

async def run_test_suite_task(
    ctx, 
    job_id: str, 
    test_cases_raw: list, 
    base_url: str, 
    auth_data: dict = None,
    model_name: str = None
):
    """The background task executed by the arq worker."""
    # 1. Get dependencies from context
    runner: TestSuiteRunner = ctx['runner']
    messaging = ctx['messaging']
    
    # Convert raw dicts back to Pydantic models
    test_cases = [TestCase(**tc) for tc in test_cases_raw]
    
    # 2. Execute
    try:
        await runner.run_suite(test_cases, base_url, job_id, auth_data, model_name)
    except Exception as e:
        # Notify about failure
        await messaging.publish_event(job_id, {"type": "ERROR", "payload": {"message": str(e)}})
        raise e

# --- Worker Settings ---

class WorkerSettings:
    """Settings used by the arq worker process."""
    functions = [run_test_suite_task]
    redis_settings = RedisSettings.from_dsn(settings.worker.redis_url)
    
    # Arq expects redis_settings to be a RedisConfig instance or URL
    # We will use the URL from our config
    on_startup = on_startup
    on_shutdown = on_shutdown
    
    # Concurrency control
    max_jobs = settings.worker.concurrency
