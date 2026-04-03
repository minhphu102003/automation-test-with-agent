from typing import Any, Optional, Tuple
from src.domain.interfaces.agent import IAgent, IBrowser
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.langfuse_logger import LangfuseBrowserLogger

class RunAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = LangfuseBrowserLogger(experiment_name=experiment_name)

    async def execute(
        self, 
        task: str, 
        model_name: str = "gpt-4o-mini", 
        url: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None
    ) -> Tuple[str, Any]:
        browser = create_browser(headless=False)
        
        # Pre-execution Auth Setup
        if url or cookies or access_token:
            print(f"--- Setting up Auth for {url or 'current page'} ---")
            # Get default session (browser-use 0.12+)
            session = await browser._browser.get_session()
            
            if url:
                await session.navigate_to(url)
            
            if cookies:
                # Convert simple map to browser-use/playwright cookie format
                # We use the current URL or provided URL for the cookie domain/path
                target_url = url or (await session.get_current_page()).url
                browser_cookies = [
                    {"name": k, "value": v, "url": target_url} 
                    for k, v in cookies.items()
                ]
                await session.add_cookies(browser_cookies)
                
            if access_token:
                # Set token in localStorage. We use 'token' as default key.
                page = await session.get_current_page()
                await page.evaluate(f"localStorage.setItem('token', '{access_token}')")
            
            if url and (cookies or access_token):
                # Reload to ensure the injected auth is picked up by the site
                await session.navigate_to(url)

        llm = create_llm(model_name)
        agent = create_agent(task, llm, browser)

        print(f"--- Executing Use Case: {task[:30]}... ---")
        history = await agent.run()
        
        # Langfuse logging
        run_id = "trace-generated-via-langfuse"
        try:
            self.logger.log_run(task, model_name, agent._history)
        except Exception as e:
            print(f"Logging Error: {e}")

        await browser.kill()
        return run_id, history
