import asyncio
from src.application.use_cases.run_automation import RunAutomationUseCase

async def run_google_search_test():
    """Specific test scenario using Clean Architecture Use Case."""
    task = "Go to google.com and search for 'browser-use python library', then tell me the first result title."
    model_name = "gpt-4o-mini"
    
    use_case = RunAutomationUseCase(experiment_name="Browser Automation Tests")
    
    print(f"--- Starting Test via UseCase: {task[:30]}... ---")
    history = await use_case.execute(task, model_name)
    
    return history
