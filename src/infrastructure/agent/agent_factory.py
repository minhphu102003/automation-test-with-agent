from browser_use import Agent, Browser
from typing import Any
from src.infrastructure.agent.browser_use_wrapper import BrowserUseAgentWrapper, BrowserUseBrowserWrapper

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

import os

def create_browser(headless: bool = False, storage_state: str = None) -> BrowserUseBrowserWrapper:
    """Initialize a Browser instance and wrap it."""
    cdp_url = os.getenv("BROWSER_CDP_URL")
    
    kwargs = {}
    if cdp_url:
        kwargs["cdp_url"] = cdp_url
    else:
        kwargs["headless"] = headless
        
    if storage_state:
        kwargs["storage_state"] = storage_state
        
    browser = Browser(**kwargs)
        
    return BrowserUseBrowserWrapper(browser)

def create_agent(task: str, llm: Any, browser: BrowserUseBrowserWrapper, result_type: Any = None, save_screenshots: bool = True) -> BrowserUseAgentWrapper:
    """Initialize a browser-use Agent and wrap it."""
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser._browser, # Accessing internal browser for browser-use
        result_type=result_type,
        save_screenshots=save_screenshots
    )
    return BrowserUseAgentWrapper(agent)
