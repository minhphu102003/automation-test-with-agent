from typing import Any, Optional, Tuple
from src.domain.interfaces.agent import IAgent, IBrowser
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.mlflow_logger import MLflowBrowserLogger

class RunAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = MLflowBrowserLogger(experiment_name=experiment_name)

    async def execute(self, task: str, model_name: str = "gpt-4o-mini") -> Tuple[str, Any]:
        browser = create_browser(headless=False)
        llm = create_llm(model_name)
        agent = create_agent(task, llm, browser)

        print(f"--- Executing Use Case: {task[:30]}... ---")
        history = await agent.run()
        
        run_id = "unknown"
        try:
            # log_run now returns the cost, but we want the run_id if possible
            # Standard MLflow setup logs to the active run
            import mlflow
            active_run = mlflow.active_run()
            if active_run:
                run_id = active_run.info.run_id
                
            self.logger.log_run(task, model_name, agent._history)
        except Exception as e:
            print(f"Logging Error: {e}")

        await browser.kill()
        return run_id, history
