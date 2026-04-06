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
from src.infrastructure.monitoring.langfuse_logger import LangfuseBrowserLogger
from src.application.services.task_analyzer import LLMTaskAnalyzer
from config.pricing import DEFAULT_MODEL

class RunExcelAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = LangfuseBrowserLogger(experiment_name=experiment_name)

    async def execute(self, file_path: str, url: str, access_token: str, cookies: str = None, model_name: str = DEFAULT_MODEL, use_vision: bool = None, max_steps: int = 5, wait_for_url: str = None, wait_for_selector: str = None) -> Tuple[str, str]:
        # 1. Setup Storage State (Cookies/Local Storage)
        storage_state_path = None
        
        # Use existing logic for access_token, and extend with cookies
        if access_token or cookies:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            origin_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Initial state structure
            state = {
                "cookies": [],
                "origins": [
                    {
                        "origin": origin_url,
                        "localStorage": []
                    }
                ]
            }
            
            # Add Access Token to localStorage if provided
            if access_token:
                state["origins"][0]["localStorage"].extend([
                    {"name": "access_token", "value": access_token},
                    {"name": "accessToken", "value": access_token},
                    {"name": "token", "value": access_token}
                ])
            
            # Add Cookies if provided (expecting JSON string {"name": "value"})
            if cookies:
                try:
                    cookie_dict = json.loads(cookies)
                    if isinstance(cookie_dict, dict):
                        for name, value in cookie_dict.items():
                            state["cookies"].append({
                                "name": name,
                                "value": str(value),
                                "url": url
                            })
                    elif isinstance(cookie_dict, list):
                        # Support direct list if provided
                        state["cookies"].extend(cookie_dict)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse cookies JSON: {cookies}")
            
            # Create temporary storage state file
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
            
        # 3.1 Preprocessing: Prepare for Grouped Execution
        # We add a hidden column to track the target URL for each row and another for the original order
        df["_original_index"] = df.index
        df["_target_url"] = df.apply(lambda r: str(r.get("URL", url)).strip() if not pd.isna(r.get("URL")) else url, axis=1)
        df["_target_url"] = df["_target_url"].apply(lambda u: url if u == "nan" or not u else u)
        
        # Sort by URL to group them together
        df_sorted = df.sort_values(by="_target_url").copy()

        browser = create_browser(headless=False, storage_state=storage_state_path)
        
        # 3.5 Stabilization: Wait for URL or Selector before starting the loop
        # This ensures the browser is at a stable auth state
        target_url = wait_for_url or url
        await self._wait_until_ready(browser, target_url, wait_for_selector)
        
        llm = create_llm(model_name)
        
        # Get browser session once for the entire run
        session = await browser._browser.get_session()

        # 4. Row-by-Row Execution (Optimized Order)
        # Ensure 'Test Steps' column exists before looping
        step_col = next((col for col in ["Test Steps", "Task description", "Description"] if col in df_sorted.columns), None)
        
        last_url = None
        
        for index, row in df_sorted.iterrows():
            if not step_col or pd.isna(row[step_col]):
                continue
                
            test_id = str(row.get("Test Case ID", f"TC-{index+1}"))
            title = str(row.get("Test Case Title", "No Title"))
            steps = str(row[step_col])
            data = str(row.get("Test Data", ""))
            expected = str(row.get("Expected Result", ""))
            row_url = row["_target_url"]
                
            # Programmatic Navigation/Reload (Saves Tokens & Ensures Clean State)
            print(f"--- [Excel] Navigating to: {row_url} (Reloading/Ensuring fresh state) ---")
            await session.navigate_to(row_url)
            # Wait for stability after navigation
            await self._wait_until_ready_on_session(session, row_url, wait_for_selector)
            last_url = row_url

            # Construct optimized Prompt (Focus ONLY on steps, Guided Planning)
            task_prompt = (
                f"SYSTEM: You are a professional QA automation engineer.\n"
                f"GOAL: Execute the following PRE-DEFINED test steps strictly in order. Do not deviate unless technically required.\n"
                f"Test Data: {data}\n"
                f"STEPS TO PERFORM:\n{steps}\n\n"
                f"TIPS: Use direct actions like 'click', 'type_text', 'scroll_to', or 'extract_content' to minimize execution steps.\n"
                f"VERIFY: {expected}\n\n"
                f"Structure your final response EXACTLY as follows:\n"
                f"ACTUAL: <short description>\n"
                f"NOTES: <your thoughts>\n"
                f"STATUS: <PASS or FAIL>"
            )
            
            print(f"--- [Excel] Executing Row {index+1}: {test_id} ---")
            
            # Smart Vision Logic
            row_use_vision = use_vision
            if row_use_vision is None:
                analyzer = LLMTaskAnalyzer()
                row_use_vision = await analyzer.requires_vision(task_prompt)
                print(f"--- [Excel] Smart Vision Decision: {'ENABLED' if row_use_vision else 'DISABLED'} ---")

            agent = create_agent(task_prompt, llm, browser, use_vision=row_use_vision, max_steps=max_steps)
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

            # Update original DF using our tracker
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
        # Restore original order and cleanup temporary columns
        df = df.sort_values(by="_original_index").drop(columns=["_original_index", "_target_url"])
        
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

    async def _wait_until_ready_on_session(self, session, url: str, selector: str = None, timeout: int = 30):
        """Wait for the page to reach a stable state using an existing session."""
        import asyncio
        if not url and not selector:
            return

        print(f"--- [Excel] Waiting for Stabilization (Timeout: {timeout}s) ---")
        page = await session.get_current_page()
        
        try:
            if url:
                print(f"--- [Excel] Waiting for URL: {url} ---")
                start_time = asyncio.get_event_loop().time()
                while asyncio.get_event_loop().time() - start_time < timeout:
                    current_url = page.url
                    if url in current_url:
                        print(f"--- [Excel] Target URL reached: {current_url} ---")
                        break
                    await asyncio.sleep(1)
                else:
                    print(f"--- [Excel] Warning: Timeout reached waiting for URL {url}. Current: {page.url} ---")

            if selector:
                print(f"--- [Excel] Waiting for Selector: {selector} ---")
                await page.wait_for_selector(selector, state="visible", timeout=timeout * 1000)
                print(f"--- [Excel] Selector {selector} is visible ---")

        except Exception as e:
            print(f"--- [Excel] Stabilization Error: {e} ---")

    async def _wait_until_ready(self, browser, url: str, selector: str = None, timeout: int = 30):
        """Wait for the page to reach a stable state (URL and/or Selector)."""
        # In Excel case, we need to get a session first
        session = await browser._browser.get_session()
        await self._wait_until_ready_on_session(session, url, selector, timeout)
