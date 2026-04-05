import asyncio
from typing import Any, Optional, Dict, Tuple
from browser_use import Tools, ActionResult
from config.pricing import DEFAULT_MODEL
from src.application.services.task_analyzer import LLMTaskAnalyzer
from src.domain.interfaces.agent import IAgent, IBrowser
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.langfuse_logger import LangfuseBrowserLogger

class RunAutomationUseCase:
    def __init__(self, experiment_name: str = "Browser Automation Tests"):
        self.logger = LangfuseBrowserLogger(experiment_name=experiment_name)

    async def execute(
        self, 
        task: str, 
        model_name: str = DEFAULT_MODEL, 
        url: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None,
        token_key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        is_mobile: Optional[bool] = False,
        use_vision: Optional[bool] = None,
        max_steps: int = 5,
        wait_for_url: Optional[str] = None,
        wait_for_selector: Optional[str] = None
    ) -> Tuple[str, Any]:
        browser = create_browser(headless=False)
        
        # browser-use 0.12.x: BrowserSession IS the session directly.
        # We need to start it before interacting.
        session = browser._browser
        await session.start()
        
        # Pre-execution Auth Setup
        if url or cookies or access_token:
            print(f"--- Setting up Auth for {url or 'current page'} ---")
            
            if url:
                await session.navigate_to(url)
            
            if cookies:
                # Inject cookies via the Playwright page context
                page = await session.get_current_page()
                target_url = url or page.url
                browser_cookies = [
                    {"name": k, "value": v, "url": target_url} 
                    for k, v in cookies.items()
                ]
                context = page.context
                await context.add_cookies(browser_cookies)
                
            if access_token:
                # Set token in localStorage. Fix: Must use arrow function syntax for browser-use
                page = await session.get_current_page()
                
                # If a specific key is provided, use only that.
                # Otherwise, set multiple common keys to be flexible.
                keys = [token_key] if token_key else ["token", "accessToken", "access_token"]
                
                for key in keys:
                    print(f"--- Setting localStorage key: {key} ---")
                    await page.evaluate(
                        "(args) => localStorage.setItem(args.key, args.val)", 
                        {"key": key, "val": access_token}
                    )
            
            if url and (cookies or access_token):
                # Reload to ensure the injected auth is picked up by the site
                await session.navigate_to(url)

        # Viewport Setup
        if width or height:
            page = await session.get_current_page()
            print(f"--- Setting Viewport: {width or 1280}x{height or 800} ---")
            await page.set_viewport_size(width=width or 1280, height=height or 800)

        # Stabilization: Wait for URL or Selector before starting Agent
        # If no wait_for_url is provided but url is, we default to waiting for that url
        target_url = wait_for_url or url
        await self._wait_until_ready(session, target_url, wait_for_selector)

        # Register Custom Tools for Responsive Testing
        tools = Tools()

        @tools.action(description='Set the browser viewport size (e.g. for mobile/desktop testing)')
        async def set_viewport(width: int, height: int):
            page = await session.get_current_page()
            print(f"--- Action: set_viewport({width}, {height}) ---")
            await page.set_viewport_size(width=width, height=height)
            return ActionResult(extracted_content=f"Viewport set to {width}x{height}")

        # Smart Vision Detection if not explicitly provided
        if use_vision is None:
            analyzer = LLMTaskAnalyzer()
            use_vision = await analyzer.requires_vision(task)
            print(f"--- Smart Vision Decision: {'ENABLED' if use_vision else 'DISABLED'} ---")

        llm = create_llm(model_name)
        agent = create_agent(task, llm, browser, tools=tools, use_vision=use_vision, max_steps=max_steps)

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

    async def _wait_until_ready(self, session, url: Optional[str], selector: Optional[str], timeout: int = 30):
        """Wait for the page to reach a stable state (URL and/or Selector)."""
        if not url and not selector:
            return

        print(f"--- Waiting for Stabilization (Timeout: {timeout}s) ---")
        page = await session.get_current_page()
        
        try:
            if url:
                print(f"--- Waiting for URL: {url} ---")
                start_time = asyncio.get_event_loop().time()
                while asyncio.get_event_loop().time() - start_time < timeout:
                    current_url = await page.get_url()
                    if url in current_url:
                        print(f"--- Target URL reached: {current_url} ---")
                        break
                    await asyncio.sleep(1)
                else:
                    print(f"--- Warning: Timeout reached waiting for URL {url}. Current: {await page.get_url()} ---")

            if selector:
                print(f"--- Waiting for Selector: {selector} ---")
                await page.wait_for_selector(selector, state="visible", timeout=timeout * 1000)
                print(f"--- Selector {selector} is visible ---")

        except Exception as e:
            print(f"--- Stabilization Error: {e} ---")

