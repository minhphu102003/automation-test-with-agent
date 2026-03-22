import asyncio
from src.core.agent_factory import create_llm, create_browser, create_agent
from src.monitoring.logger import MLflowBrowserLogger
from src.utils.google_sheets import GoogleSheetsClient

async def run_data_driven_test(spreadsheet_name: str):
    """
    Data-driven test scenario: 
    Reads tasks from Google Sheets and executes them sequentially.
    """
    client = GoogleSheetsClient()
    
    try:
        print(f"--- Fetching test data from Google Sheet: {spreadsheet_name} ---")
        test_cases = client.get_sheet_data(spreadsheet_name)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    logger = MLflowBrowserLogger(experiment_name="Data-Driven Browser Tests")
    browser = create_browser(headless=False)
    
    for i, row in enumerate(test_cases):
        task = row.get('task')
        model_name = row.get('model', 'gpt-4o-mini')
        
        if not task:
            print(f"Skipping row {i+1}: No task description found.")
            continue
            
        print(f"\n[TestCase {i+1}] Executing: {task}")
        
        llm = create_llm(model_name)
        agent = create_agent(task, llm, browser)
        
        history = await agent.run()
        
        # Log to MLflow
        try:
            total_cost = logger.log_run(f"Data-Driven: {task[:50]}", model_name, history)
            print(f"Logged to MLflow. Cost: ${total_cost:.6f}")
        except Exception as e:
            print(f"MLflow Logging Error: {e}")
            
        is_success = history.is_successful()
        print(f"Result: {'Success' if is_success else 'Failure'}")
        
        # Optional: Write status back to Google Sheets
        # cell_to_update = f"D{i+2}" # Assuming Status is in column D
        # client.update_cell(spreadsheet_name, cell_to_update, "PASSED" if is_success else "FAILED")

    await browser.kill()
    print("\n--- Data-Driven Suite Completed ---")
