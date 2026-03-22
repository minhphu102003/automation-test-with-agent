import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

async def main():
    # 1. Configure the browser
    # headless=False allows you to see the browser in action
    browser = Browser(
        config=BrowserConfig(
            headless=False,
        )
    )

    # 2. Initialize the LLM
    # Note: Ensure OPENAI_API_KEY is set in your .env or environment
    llm = ChatOpenAI(model="gpt-4o")

    # 3. Create the Agent
    agent = Agent(
        task="Go to google.com and search for 'browser-use python library', then tell me the first result title.",
        llm=llm,
        browser=browser,
    )

    # 4. Run the agent
    result = await agent.run()
    print("\n--- Agent Result ---")
    print(result)

    # 5. Close the browser
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
