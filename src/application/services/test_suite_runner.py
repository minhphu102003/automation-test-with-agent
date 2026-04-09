import asyncio
import base64
import uuid
import logging
from typing import List, Dict, Any, Optional
from src.domain.interfaces.agent import IBrowser
from src.domain.interfaces.storage import IStorageService
from src.domain.interfaces.messaging import IEventStreamService
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.presentation.schemas.automation import TestCase
from src.infrastructure.config.loader import settings

logger = logging.getLogger(__name__)

class TestSuiteRunner:
    """Core engine to run a suite of tests and report progress via event streams."""
    
    def __init__(
        self, 
        storage: IStorageService, 
        messaging: IEventStreamService,
        job_id: str
    ):
        self.storage = storage
        self.messaging = messaging
        self.job_id = job_id
        self.conf = settings.agent

    async def run_suite(
        self, 
        test_cases: List[TestCase], 
        base_url: str,
        auth_data: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None
    ) -> List[TestCase]:
        model_name = model_name or self.conf.default_model
        
        # 1. Initialize Browser
        logger.info(f"--- [Job {self.job_id}] Initializing Browser ---")
        await self._notify("RUNNER_INIT", {"message": "Initializing browser and authentication..."})
        
        browser = create_browser(headless=True)
        try:
            session = await browser._browser.get_session()
            
            # 2. Execution Loop
            total = len(test_cases)
            for idx, tc in enumerate(test_cases):
                await self._notify("TEST_STARTED", {
                    "test_id": tc.id,
                    "title": tc.title,
                    "index": idx + 1,
                    "total": total
                })
                
                # Navigate and stabilize
                target_url = tc.url or base_url
                logger.info(f"--- [Job {self.job_id}] Running TC {idx+1}/{total}: {tc.title} ---")
                await session.navigate_to(target_url)
                
                # Execution logic (similar to RunExcelAutomationUseCase)
                task_prompt = self._build_prompt(tc)
                llm = create_llm(model_name)
                agent = create_agent(task_prompt, llm, browser, use_vision=self.conf.use_vision, max_steps=self.conf.max_steps)
                
                history = await agent.run()
                
                # Process Results
                final_text = history.final_result() if history else "No result"
                tc.status = "Pass" if "STATUS: PASS" in final_text else "Fail"
                tc.actual = self._extract_actual_result(final_text)
                
                # Capture and Upload Evidence
                evidence_url = await self._capture_evidence(history, tc.id)
                tc.comments = evidence_url # Store URL in comments for now
                
                await self._notify("TEST_COMPLETED", {
                    "test_id": tc.id,
                    "status": tc.status,
                    "actual_result": tc.actual,
                    "evidence_url": evidence_url
                })

            await self._notify("RUNNER_FINISHED", {"message": "All test cases completed."})
            return test_cases

        finally:
            await browser.kill()

    async def _notify(self, type: str, data: Dict[str, Any]):
        """Helper to send updates to the Redis stream."""
        await self.messaging.publish_event(self.job_id, {"type": type, "payload": data})

    async def _capture_evidence(self, history, test_id: str) -> Optional[str]:
        """Captures last screenshot and uploads to storage."""
        if history and hasattr(history, 'history') and len(history.history) > 0:
            last_state = history.history[-1].state
            if last_state and hasattr(last_state, 'screenshot') and last_state.screenshot:
                try:
                    img_data = base64.b64decode(last_state.screenshot)
                    filename = f"jobs/{self.job_id}/{test_id}_evidence.png"
                    url = await self.storage.upload_file(img_data, filename)
                    return url
                except Exception as e:
                    logger.error(f"Failed to upload evidence for {test_id}: {e}")
        return None

    def _build_prompt(self, tc: TestCase) -> str:
        return (
            f"GOAL: Execute the following test steps strictly.\n"
            f"Test Data: {tc.data}\n"
            f"STEPS:\n{tc.steps}\n\n"
            f"VERIFY: {tc.expected}\n\n"
            f"Output exact format:\nACTUAL: <text>\nSTATUS: <PASS or FAIL>"
        )

    def _extract_actual_result(self, text: str) -> str:
        for line in text.split('\n'):
            if line.startswith("ACTUAL:"):
                return line.replace("ACTUAL:", "").strip()
        return text.split('\n')[0][:200]
