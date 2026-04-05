import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from src.core.agent_factory import create_llm, create_browser, create_agent
from src.monitoring.logger import MLflowBrowserLogger
from config.pricing import DEFAULT_MODEL
from src.utils.google_sheets import GoogleSheetsClient
from src.utils.google_drive import GoogleDriveClient
from src.prompts.test_case_prompts import build_agent_prompt, TestCaseResult
from src.monitoring.report_generator import generate_html_report, generate_pdf_report

load_dotenv()

async def run_structured_tests(spreadsheet_id_or_url: str, worksheet_name: str = None, project_name: str = None):
    """
    Runner for structured test cases from Google Sheets.
    """
    client = GoogleSheetsClient()
    drive_client = GoogleDriveClient()
    logger = MLflowBrowserLogger(experiment_name="Structured Browser Tests")
    browser = create_browser(headless=False)
    
    try:
        print(f"--- Fetching Structured Test Cases ---")
        # Use internal helper to open and get actual title if project_name not provided
        spreadsheet = client._open_spreadsheet(spreadsheet_id_or_url)
        actual_project_name = project_name or spreadsheet.title
        
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
            
        test_cases = worksheet.get_all_records()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # To store results for final report
    final_results = []
    
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    for i, row in enumerate(test_cases):
        test_id = row.get("Test Case ID") or row.get("ID")
        if not test_id:
            print(f"Skipping row {i+1}: Missing Test Case ID.")
            continue
            
        print(f"\n[{test_id}] {row.get('Test Case Title')}")
        
        # Build prompt and initialize agent
        task_prompt = build_agent_prompt(row)
        model_name = row.get('model', DEFAULT_MODEL) 
        
        llm = create_llm(model_name)
        # Pass TestCaseResult as result_type to get structured output
        agent = create_agent(task_prompt, llm, browser, result_type=TestCaseResult)
        
        # Run agent
        history = await agent.run()
        
        # Capture final screenshot (evidence)
        evidence_path = ""
        evidence_formula = ""
        screenshots = history.screenshot_paths()
        if screenshots:
            local_path = screenshots[-1]
            evidence_path = local_path
            
            # Upload to Google Drive and get link
            try:
                print(f"Uploading screenshot to Google Drive...")
                # Organize folders: Project -> Module
                project_folder_id = drive_client.get_or_create_folder(actual_project_name)
                module_name = row.get("Module / Feature") or "General"
                module_folder_id = drive_client.get_or_create_folder(module_name, parent_id=project_folder_id)
                
                # Use Test Case ID as filename
                ext = os.path.splitext(local_path)[1]
                custom_filename = f"{test_id}{ext}"
                
                drive_link = drive_client.upload_file(local_path, folder_id=module_folder_id, custom_name=custom_filename)
                
                # Use =IMAGE() formula for in-cell display
                evidence_formula = f'=IMAGE("{drive_link}")'
                print(f"Screenshot uploaded to {actual_project_name}/{module_name} as {custom_filename}")
            except Exception as e:
                print(f"Google Drive Upload Error: {e}")
                evidence_formula = local_path # Fallback to local path string
            
        # Extract structured result from history.final_result()
        result = history.final_result()
        
        if result and isinstance(result, TestCaseResult):
            actual_result = result.actual_result
            status = result.status
            comments = result.comments or ""
        else:
            is_success = history.is_successful()
            status = "Pass" if is_success else "Fail"
            actual_result = "Test execution completed. "
            if history.final_result():
                actual_result += str(history.final_result())
            comments = "Note: Structured result extraction might have failed."
            
        print(f"Result: {status}")
        
        # Log to MLflow
        try:
            logger.log_run(f"{test_id}: {row.get('Test Case Title')[:50]}", model_name, history)
        except Exception as e:
            print(f"MLflow Logging Error: {e}")

        # Update Google Sheet
        results_to_update = {
            "Actual Result": actual_result,
            "Status (Pass/Fail)": status,
            "Evidence": evidence_formula,
            "Comments / Notes": f"{comments} | Executed by AI Agent using {model_name}".strip(" | ")
        }
        
        try:
            client.update_row_results(spreadsheet_id_or_url, test_id, results_to_update, worksheet_name)
            print(f"Updated Google Sheet for {test_id}")
        except Exception as e:
            print(f"Error updating sheet: {e}")

        # Collect for HTML/PDF Report (use local path for offline viewing)
        row_report = row.copy()
        row_report.update(results_to_update)
        row_report["Evidence"] = evidence_path 
        final_results.append(row_report)

    await browser.kill()
    
    # Generate HTML & PDF Reports
    if final_results:
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_report_path = f"reports/report_{timestamp_str}.html"
        pdf_report_path = f"reports/report_{timestamp_str}.pdf"
        
        generate_html_report(final_results, html_report_path)
        await generate_pdf_report(html_report_path, pdf_report_path)
        
        print(f"\n✅ Total {len(final_results)} tests processed. Reports generated.")

    print("\n--- Structured Test Suite Completed ---")

if __name__ == "__main__":
    SHEET_NAME = os.getenv("TEST_SPREADSHEET_NAME", "Automation Test Cases")
    asyncio.run(run_structured_tests(SHEET_NAME))
