from typing import Any, Optional, Tuple
from src.domain.interfaces.agent import IAgent, IBrowser
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.langfuse_logger import LangfuseBrowserLogger

class RunAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = LangfuseBrowserLogger(experiment_name=experiment_name)

    async def execute(self, task: str, model_name: str = "gpt-4o-mini") -> Tuple[str, Any]:
        browser = create_browser(headless=False)
        llm = create_llm(model_name)
        agent = create_agent(task, llm, browser)

        print(f"--- Executing Use Case: {task[:30]}... ---")
        history = await agent.run()
        
        # Langfuse returns the cost, but trace id is handled internally unless specified
        run_id = "trace-generated-via-langfuse"
        try:
            self.logger.log_run(task, model_name, agent._history)
        except Exception as e:
            print(f"Logging Error: {e}")

        await browser.kill()
        return run_id, history
