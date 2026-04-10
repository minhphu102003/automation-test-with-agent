import uuid
import logging
from arq import create_pool
from src.application.services.gpt_bridge import GPTBridgeService
from src.infrastructure.config.loader import settings
from src.presentation.schemas.automation import TestCase

logger = logging.getLogger(__name__)

class RunGptAutomationUseCase:
    """Use case to parse GPT text and enqueue an automation job."""
    
    def __init__(self, gpt_service: GPTBridgeService):
        self.gpt_service = gpt_service

    async def execute(
        self, 
        raw_text: str, 
        base_url: str = "https://www.google.com",
        model_name: str = None
    ) -> str:
        # 1. Parse GPT Output
        logger.info("--- [GPT Use Case] Parsing raw text ---")
        test_cases = self.gpt_service.parse_gpt_output(raw_text)
        
        if not test_cases:
            raise ValueError("Could not parse any test cases from the provided text.")

        # 2. Generate Job ID
        job_id = str(uuid.uuid4())[:12]
        
        # 3. Enqueue Job in Arq
        # We store dicts in the queue because Pydantic models aren't always JSON serializable for Arq
        test_cases_data = [tc.model_dump(by_alias=True) for tc in test_cases]
        
        from arq.connections import RedisSettings
        # Parse redis url for arq settings if needed, but create_pool usually takes RedisSettings
        # We'll use the URL directly as create_pool also supports it in some versions 
        # but let's be safe and use RedisSettings
        
        redis_pool = await create_pool(settings.worker.redis_url)
        try:
            await redis_pool.enqueue_job(
                'run_test_suite_task',
                job_id,
                test_cases_data,
                base_url,
                model_name=model_name,
                _job_id=job_id # Also set arq's internal job id
            )
            logger.info(f"--- [GPT Use Case] Job {job_id} enqueued ---")
            return job_id
        finally:
            await redis_pool.close()
