# ruff: noqa: E402

import sys
import types
import unittest
from unittest.mock import patch

fake_browser_use = types.ModuleType("browser_use")


class _FakeTools:
    def action(self, description):
        def decorator(func):
            return func

        return decorator


class _FakeActionResult:
    def __init__(self, extracted_content=None):
        self.extracted_content = extracted_content


class _Placeholder:
    def __init__(self, *args, **kwargs):
        pass


fake_browser_use.Tools = _FakeTools
fake_browser_use.ActionResult = _FakeActionResult
fake_browser_use.AgentHistoryList = object
fake_browser_use.Agent = _Placeholder
fake_browser_use.BrowserSession = _Placeholder
fake_browser_use.BrowserProfile = _Placeholder
fake_browser_use.ChatOpenAI = _Placeholder
fake_browser_use.ChatGoogle = _Placeholder
sys.modules.setdefault("browser_use", fake_browser_use)

fake_langfuse = types.ModuleType("langfuse")


class _FakeLangfuse:
    def trace(self, **kwargs):
        return self

    def generation(self, **kwargs):
        return None

    def flush(self):
        return None


fake_langfuse.Langfuse = _FakeLangfuse
sys.modules.setdefault("langfuse", fake_langfuse)

fake_langchain_openai = types.ModuleType("langchain_openai")


class _FakeChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass


fake_langchain_openai.ChatOpenAI = _FakeChatOpenAI
sys.modules.setdefault("langchain_openai", fake_langchain_openai)

from src.application.use_cases.run_automation import RunAutomationUseCase
from src.domain.entities.auth_profile import ResolvedAuthProfile


class _FakeContext:
    def __init__(self) -> None:
        self.cookies = []

    async def add_cookies(self, cookies):
        self.cookies.extend(cookies)


class _FakePage:
    def __init__(self) -> None:
        self.context = _FakeContext()
        self.url = "https://example.com/app"
        self.evaluations = []
        self.viewport = None

    async def evaluate(self, script, payload):
        self.evaluations.append((script, payload))

    async def set_viewport_size(self, width, height):
        self.viewport = (width, height)

    async def get_url(self):
        return self.url

    async def wait_for_selector(self, selector, state, timeout):
        return None


class _FakeSession:
    def __init__(self) -> None:
        self.page = _FakePage()
        self.started = False
        self.navigations = []

    async def start(self):
        self.started = True

    async def navigate_to(self, url):
        self.navigations.append(url)
        self.page.url = url

    async def get_current_page(self):
        return self.page


class _FakeBrowser:
    def __init__(self) -> None:
        self._browser = _FakeSession()
        self.killed = False

    async def kill(self):
        self.killed = True


class _FakeHistory:
    def final_result(self):
        return "done"


class _FakeAgent:
    def __init__(self) -> None:
        self._history = []

    async def run(self):
        return _FakeHistory()


class _FakeProfileManager:
    async def resolve_auth_profile(self, profile_id: str) -> ResolvedAuthProfile:
        return ResolvedAuthProfile(
            profile_id=profile_id,
            name="Staging",
            url="https://example.com/app",
            access_token="fresh-token",
            cookies={"session": "cookie-123"},
            token_key="custom_token",
        )


class RunAutomationUseCaseTest(unittest.IsolatedAsyncioTestCase):
    async def test_execute_resolves_profile_and_injects_auth_into_browser(self) -> None:
        fake_browser = _FakeBrowser()
        use_case = RunAutomationUseCase(profile_manager=_FakeProfileManager())
        use_case.logger = type("Logger", (), {"log_run": lambda *args, **kwargs: None})()

        with (
            patch("src.application.use_cases.run_automation.create_browser", return_value=fake_browser),
            patch("src.application.use_cases.run_automation.create_llm", return_value=object()),
            patch("src.application.use_cases.run_automation.create_agent", return_value=_FakeAgent()),
        ):
            run_id, _ = await use_case.execute(
                task="Open dashboard",
                model_name="gpt-4o-mini",
                profile_id="staging",
                use_vision=False,
            )

        page = fake_browser._browser.page
        self.assertEqual("trace-generated-via-langfuse", run_id)
        self.assertTrue(fake_browser._browser.started)
        self.assertTrue(fake_browser.killed)
        self.assertEqual(
            [
                "https://example.com/app",
                "https://example.com/app",
            ],
            fake_browser._browser.navigations,
        )
        self.assertEqual("session", page.context.cookies[0]["name"])
        self.assertEqual("cookie-123", page.context.cookies[0]["value"])
        self.assertEqual(
            {"key": "custom_token", "val": "fresh-token"},
            page.evaluations[0][1],
        )
