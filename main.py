import asyncio
import os
from dotenv import load_dotenv

# Import our refactored tests
from tests.google_search_test import run_google_search_test
from tests.data_driven_test import run_data_driven_test

# Load environment variables
load_dotenv()

async def main():
    """Central entry point to run automation tests."""
    print("=== Browser-Use Automation Test Suite ===")
    
    # 1. Standard Test Scenario
    await run_google_search_test()

    # 2. Data-Driven Scenario (Requires credentials.json and a sheet named 'AutomationTasks')
    # await run_data_driven_test("AutomationTasks")

if __name__ == "__main__":
    asyncio.run(main())
