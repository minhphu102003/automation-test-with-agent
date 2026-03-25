from typing import Any, Optional
from src.domain.interfaces.agent import IAgent, IBrowser
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.mlflow_logger import MLflowBrowserLogger

class RunAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = MLflowBrowserLogger(experiment_name=experiment_name)

    async def execute(self, task: str, model_name: str = "gpt-4o-mini") -> Any:
        browser = create_browser(headless=False)
        llm = create_llm(model_name)
        agent = create_agent(task, llm, browser)

        print(f"--- Executing Use Case: {task[:30]}... ---")
        history = await agent.run()
        
        try:
            # Note: We need to pass the raw browser-use history to the logger for now
            self.logger.log_run(task, model_name, agent._history)
        except Exception as e:
            print(f"Logging Error: {e}")

        final_result = agent.final_result()
        print(f"UseCase Result: {final_result}")
        
        await browser.kill()
        return history
