import os
from typing import Any
from browser_use import Agent, BrowserSession, BrowserProfile, ChatOpenAI, ChatGoogle
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
    """Initialize a BrowserSession instance and wrap it.
    
    NOTE: browser-use 0.12.x replaced Browser/BrowserConfig with BrowserSession/BrowserProfile.
    """
    cdp_url = os.getenv("BROWSER_CDP_URL")
    
    kwargs = {
        "headless": headless,
    }
    
    if cdp_url:
        kwargs["cdp_url"] = cdp_url
        
    browser = BrowserSession(**kwargs)
        
    return BrowserUseBrowserWrapper(browser)

def create_agent(
    task: str, 
    llm: Any, 
    browser: BrowserUseBrowserWrapper, 
    result_type: Any = None, 
    tools: Any = None,
    use_vision: bool = True,
    max_steps: int = 5,
    save_screenshots: bool = False # Set False for cost optimization
) -> BrowserUseAgentWrapper:
    """Initialize a browser-use Agent and wrap it.
    
    NOTE: browser-use 0.12.x removed BrowserContextConfig.
    Agent now accepts browser_session directly.
    """
    # COST OPTIMIZATION: use_vision=False reduces token consumption
    # COST OPTIMIZATION: max_steps=5 prevents runaway token usage
    
    agent = Agent(
        task=task,
        llm=llm,
        browser_session=browser._browser,
        use_vision=use_vision,
        max_steps=max_steps,
        tools=tools,
    )
    return BrowserUseAgentWrapper(agent)
