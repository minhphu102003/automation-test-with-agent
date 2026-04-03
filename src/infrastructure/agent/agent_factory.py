import os
from typing import Any
from browser_use import Agent, Browser, ChatOpenAI, ChatGoogle
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from src.infrastructure.agent.browser_use_wrapper import BrowserUseAgentWrapper, BrowserUseBrowserWrapper

def create_llm(model_name: str):
    """Factory to create the appropriate LLM wrapper based on model name."""
    if model_name.startswith("gpt"):
        return ChatOpenAI(model=model_name)
    elif "nano" in model_name or "gemini" in model_name:
        return ChatGoogle(model=model_name)
    else:
        return ChatOpenAI(model=model_name)

def create_browser(headless: bool = False, storage_state: str = None) -> BrowserUseBrowserWrapper:
    """Initialize a Browser instance and wrap it."""
    cdp_url = os.getenv("BROWSER_CDP_URL")
    
    # COST OPTIMIZATION: Use Adblock and disable highlighting to reduce DOM noise
    # Also exclude non-essential elements to focus on the content
    config = BrowserConfig(
        headless=headless,
        disable_gpu=True,
        # highlight_elements=False,
    )
    
    # DOM CLEANING: Focus on the chat/main content areas
    # We exclude common non-interactive or distracting elements
    context_kwargs = {
        "browser_context_config": {
            "excluded_selectors": [
                "nav", "footer", "header", "aside", 
                ".ad", ".ads", ".sidebar", ".cookie-banner",
                "script", "style", "noscript", "svg", "iframe"
            ]
        }
    }
    
    kwargs = {}
    if cdp_url:
        kwargs["cdp_url"] = cdp_url
    else:
        # Check if version supports BrowserConfig
        try:
            kwargs["config"] = config
        except Exception:
            kwargs["headless"] = headless
        
    if storage_state:
        kwargs["storage_state"] = storage_state
        
    browser = Browser(**kwargs)
        
    return BrowserUseBrowserWrapper(browser)

def create_agent(
    task: str, 
    llm: Any, 
    browser: BrowserUseBrowserWrapper, 
    result_type: Any = None, 
    save_screenshots: bool = False # Set False for cost optimization
) -> BrowserUseAgentWrapper:
    """Initialize a browser-use Agent and wrap it."""
    # COST OPTIMIZATION: use_vision=False reduces token consumption
    # COST OPTIMIZATION: max_steps=5 prevents runaway token usage
    # DOM CLEANING: Focus on the chat/main content areas to save tokens
    
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser._browser,
        result_type=result_type,
        use_vision=False,
        max_steps=5,
        save_screenshots=save_screenshots,
        browser_context_config=BrowserContextConfig(
            excluded_selectors=[
                "nav", "footer", "header", "aside", 
                ".ad", ".ads", ".sidebar", ".cookie-banner",
                "script", "style", "noscript", "svg", "iframe"
            ]
        )
    )
    return BrowserUseAgentWrapper(agent)
