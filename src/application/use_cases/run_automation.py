import asyncio
from typing import Any, Optional, Dict, Tuple
from browser_use import Tools, ActionResult
from config.pricing import DEFAULT_MODEL
from src.application.use_cases.manage_profiles import ManageProfilesUseCase
from src.domain.exceptions.base import DomainException
from src.infrastructure.agent.agent_factory import create_llm, create_browser, create_agent
from src.infrastructure.monitoring.langfuse_logger import LangfuseBrowserLogger

class RunAutomationUseCase:
    def __init__(
        self,
        experiment_name: str = "Browser Automation Tests",
        profile_manager: Optional[ManageProfilesUseCase] = None,
    ):
        self.logger = LangfuseBrowserLogger(experiment_name=experiment_name)
        self.profile_manager = profile_manager

    async def execute(
        self, 
        task: str, 
        model_name: str = DEFAULT_MODEL, 
        profile_id: Optional[str] = None,
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
        try:
            # browser-use 0.12.x: BrowserSession IS the session directly.
            # We need to start it before interacting.
            session = browser._browser
            await session.start()

            if profile_id:
                if self.profile_manager is None:
                    raise DomainException("Profile manager is not configured for automation runs")
                resolved_profile = await self.profile_manager.resolve_auth_profile(profile_id)
                url = url or resolved_profile.url
                if resolved_profile.cookies:
                    cookies = {**resolved_profile.cookies, **(cookies or {})}
                if access_token is None and resolved_profile.access_token:
                    access_token = resolved_profile.access_token
                token_key = token_key or resolved_profile.token_key

            await self._setup_auth(session, url, cookies, access_token, token_key)

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
                from src.application.services.task_analyzer import LLMTaskAnalyzer

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

            return run_id, history
        finally:
            await browser.kill()

    async def _setup_auth(
        self,
        session: Any,
        url: Optional[str],
        cookies: Optional[Dict[str, str]],
        access_token: Optional[str],
        token_key: Optional[str],
    ) -> None:
        if not (url or cookies or access_token):
            return

        print(f"--- Setting up Auth for {url or 'current page'} ---")

        if url:
            await session.navigate_to(url)

        if cookies:
            page = await session.get_current_page()
            target_url = url or page.url
            browser_cookies = [
                {"name": key, "value": value, "url": target_url}
                for key, value in cookies.items()
            ]
            context = page.context
            await context.add_cookies(browser_cookies)

        if access_token:
            page = await session.get_current_page()
            keys = [token_key] if token_key else ["token", "accessToken", "access_token"]

            for key in keys:
                print(f"--- Setting localStorage key: {key} ---")
                await page.evaluate(
                    "(args) => localStorage.setItem(args.key, args.val)",
                    {"key": key, "val": access_token},
                )

        if url and (cookies or access_token):
            await session.navigate_to(url)

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
