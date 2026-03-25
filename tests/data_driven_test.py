import asyncio
from src.application.use_cases.run_automation import RunAutomationUseCase
from src.infrastructure.external.google_sheets import GoogleSheetsClient

async def run_data_driven_test(spreadsheet_name: str):
    """
    Data-driven test scenario using Clean Architecture components.
    """
    client = GoogleSheetsClient()
    
    try:
        print(f"--- Fetching test data from Google Sheet: {spreadsheet_name} ---")
        test_cases = client.get_sheet_data(spreadsheet_name)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Reusing the use case for each row
    use_case = RunAutomationUseCase(experiment_name="Data-Driven Browser Tests")
    
    for i, row in enumerate(test_cases):
        task = row.get('task')
        model_name = row.get('model', 'gpt-4o-mini')
        
        if not task:
            print(f"Skipping row {i+1}: No task description found.")
            continue
            
        print(f"\n[TestCase {i+1}] Executing: {task}")
        
        # Note: Current RunAutomationUseCase creates a new browser for each task.
        history = await use_case.execute(task, model_name)
        
        is_success = history.is_successful()
        print(f"Result: {'Success' if is_success else 'Failure'}")

    print("\n--- Data-Driven Suite Completed ---")
