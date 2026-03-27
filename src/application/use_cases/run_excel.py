import pandas as pd
import json
import tempfile
import os
import shutil
import base64
import uuid
import zipfile
from typing import Any, Tuple
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.mlflow_logger import MLflowBrowserLogger

class RunExcelAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = MLflowBrowserLogger(experiment_name=experiment_name)

    async def execute(self, file_path: str, url: str, access_token: str, model_name: str = "gpt-4o-mini") -> Tuple[str, str]:
        # 1. Setup Storage State (Cookies/Local Storage)
        storage_state_path = None
        if access_token:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            origin_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            state = {
                "cookies": [],
                "origins": [
                    {
                        "origin": origin_url,
                        "localStorage": [
                            {"name": "access_token", "value": access_token},
                            {"name": "accessToken", "value": access_token}
                        ]
                    }
                ]
            }
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir=tempfile.gettempdir()) as f:
                json.dump(state, f)
                storage_state_path = f.name
                
        # 2. Setup Results Directory
        run_id = str(uuid.uuid4())[:8]
        results_dir = os.path.join(tempfile.gettempdir(), f"excel_run_{run_id}")
        os.makedirs(results_dir, exist_ok=True)
        evidence_dir = os.path.join(results_dir, "evidence")
        os.makedirs(evidence_dir, exist_ok=True)

        # 3. Read Excel
        df = pd.read_excel(file_path)
        
        # Ensure output columns exist
        if "Actual Result" not in df.columns:
            df["Actual Result"] = ""
        if "Status (Pass/Fail)" not in df.columns:
            df["Status (Pass/Fail)"] = ""
        if "Evidence" not in df.columns:
            df["Evidence"] = ""

        browser = create_browser(headless=False, storage_state=storage_state_path)
        llm = create_llm(model_name)

        # 4. Row-by-Row Execution
        # Ensure 'Test Steps' column exists before looping
        step_col = next((col for col in ["Test Steps", "Task description", "Description"] if col in df.columns), None)
        
        for index, row in df.iterrows():
            if not step_col or pd.isna(row[step_col]):
                continue
                
            test_id = str(row.get("Test Case ID", f"TC-{index+1}"))
            title = str(row.get("Test Case Title", "No Title"))
            steps = str(row[step_col])
            data = str(row.get("Test Data", ""))
            expected = str(row.get("Expected Result", ""))
            
            # Construct strict Prompt for the Agent
            task_prompt = (
                f"You are executing Test Case: {test_id} - {title}.\n"
                f"Go to URL: {url}\n"
                f"Test Data to use: {data}\n"
                f"Test Steps to perform: {steps}\n\n"
                f"After performing the steps, verify the Expected Result: {expected}.\n"
                f"Structure your final response EXACTLY as follows:\n"
                f"ACTUAL: <short description of what actually happened>\n"
                f"NOTES: <your thoughts, reasoning, or any abnormalities found during execution>\n"
                f"STATUS: <PASS or FAIL>"
            )
            
            print(f"--- Executing Row {index+1}: {test_id} ---")
            agent = create_agent(task_prompt, llm, browser)
            history = await agent.run()
            
            # Extract final text
            final_text = history.final_result() if history else "No result"
            
            actual_res = ""
            notes_res = ""
            status_res = "Fail"
            
            if "STATUS: PASS" in final_text:
                status_res = "Pass"
                
            for line in final_text.split('\n'):
                if line.startswith("ACTUAL:"):
                    actual_res = line.replace("ACTUAL:", "").strip()
                elif line.startswith("NOTES:"):
                    notes_res = line.replace("NOTES:", "").strip()
            
            # Fallback if agent didn't follow strict format
            if not actual_res and not notes_res:
                actual_res = final_text.replace("STATUS: PASS", "").replace("STATUS: FAIL", "").strip()
            
            # Save Evidence Screenshot
            evidence_file = ""
            if history and hasattr(history, 'history') and len(history.history) > 0:
                last_state = history.history[-1].state
                if last_state and hasattr(last_state, 'screenshot') and last_state.screenshot:
                    try:
                        img_data = base64.b64decode(last_state.screenshot)
                        screenshot_name = f"{test_id}_evidence.png"
                        screenshot_path = os.path.join(evidence_dir, screenshot_name)
                        with open(screenshot_path, "wb") as f:
                            f.write(img_data)
                        evidence_file = screenshot_name
                    except Exception as e:
                        print(f"Failed to save screenshot: {e}")

            # Update DF
            df.at[index, "Actual Result"] = actual_res
            if "Comments / Notes" not in df.columns:
                df["Comments / Notes"] = ""
            df.at[index, "Comments / Notes"] = notes_res
            df.at[index, "Status (Pass/Fail)"] = status_res
            df.at[index, "Evidence"] = evidence_file

            # Log to MLflow
            try:
                self.logger.log_run(f"{test_id} ({title})", model_name, agent._history)
            except Exception as e:
                pass

        await browser.kill()
        if storage_state_path and os.path.exists(storage_state_path):
            os.remove(storage_state_path)

        # 5. Export Output Excel and Zip
        output_excel_path = os.path.join(results_dir, "output.xlsx")
        df.to_excel(output_excel_path, index=False)
        
        zip_path = os.path.join(tempfile.gettempdir(), f"excel_run_{run_id}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(output_excel_path, "output.xlsx")
            for root, dirs, files in os.walk(evidence_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.join("evidence", file))
        
        # Cleanup dir
        shutil.rmtree(results_dir)
        
        return run_id, zip_path
