import asyncio
from src.core.agent_factory import create_llm, create_browser, create_agent
from src.monitoring.logger import MLflowBrowserLogger

async def run_google_search_test():
    """Specific test scenario: Google Search for browser-use."""
    model_name = "gpt-4o-mini"
    task = "Go to google.com and search for 'browser-use python library', then tell me the first result title."
    
    logger = MLflowBrowserLogger(experiment_name="Browser Automation Tests")
    browser = create_browser(headless=False)
    llm = create_llm(model_name)
    agent = create_agent(task, llm, browser)

    print(f"--- Starting Test: {task[:30]}... ---")
    history = await agent.run()
    
    try:
        total_cost = logger.log_run(task, model_name, history)
        print(f"Test Completed. Estimated Cost: ${total_cost:.6f}")
    except Exception as e:
        print(f"Logging Error: {e}")

    final_result = history.final_result()
    print(f"Final Result: {final_result}")
    
    await browser.kill()
    return history
