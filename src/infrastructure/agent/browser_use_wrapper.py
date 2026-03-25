from typing import Any, Optional
from browser_use import Agent, Browser
from src.domain.interfaces.agent import IAgent, IBrowser

class BrowserUseAgentWrapper(IAgent):
    def __init__(self, agent: Agent):
        self._agent = agent
        self._history = None

    async def run(self) -> Any:
        self._history = await self._agent.run()
        return self._history

    def final_result(self) -> str:
        if self._history:
            return self._history.final_result()
        return ""

class BrowserUseBrowserWrapper(IBrowser):
    def __init__(self, browser: Browser):
        self._browser = browser

    async def kill(self):
        await self._browser.kill()
