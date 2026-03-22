import asyncio
import os
from dotenv import load_dotenv

# Import our refactored tests
from tests.google_search_test import run_google_search_test

# Load environment variables
load_dotenv()

async def main():
    """Central entry point to run automation tests."""
    print("=== Browser-Use Automation Test Suite ===")
    
    # In the future, you can add more tests here or use a CLI to select them
    await run_google_search_test()

if __name__ == "__main__":
    asyncio.run(main())
