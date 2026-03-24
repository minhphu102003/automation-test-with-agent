from browser_use import Agent, Browser
from typing import Any

def create_llm(model_name: str):
    """Factory to create the appropriate LLM wrapper based on model name."""
    if model_name.startswith("gpt"):
        from browser_use import ChatOpenAI
        return ChatOpenAI(model=model_name)
    elif "nano" in model_name or "gemini" in model_name:
        from browser_use import ChatGoogle
        return ChatGoogle(model=model_name)
    else:
        from browser_use import ChatOpenAI
        return ChatOpenAI(model=model_name)

def create_browser(headless: bool = False) -> Browser:
    """Initialize a Browser instance."""
    return Browser(headless=headless)

def create_agent(task: str, llm: Any, browser: Browser, result_type: Any = None, save_screenshots: bool = True) -> Agent:
    """Initialize a browser-use Agent with optional result_type and screenshot saving."""
    return Agent(
        task=task,
        llm=llm,
        browser=browser,
        result_type=result_type,
        save_screenshots=save_screenshots
    )
