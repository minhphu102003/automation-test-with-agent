import sys
import os
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Ensure src is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.monitoring.langfuse_logger import LangfuseBrowserLogger
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader

def test_langfuse_connection():
    load_dotenv()
    
    print("=== Testing Langfuse Cloud Connection & Mocking Trace ===")
    
    # 1. Mock the AgentHistoryList
    print("\n[1] Creating a mock 'browser-use' history...")
    mock_history = MagicMock()
    mock_history.history = []
    
    # Mocking standard Langchain usage tokens
    mock_usage = MagicMock()
    mock_usage.total_prompt_tokens = 1200
    mock_usage.total_completion_tokens = 400
    mock_history.usage = mock_usage
    
    mock_history.total_duration_seconds.return_value = 8.5
    mock_history.is_successful.return_value = True

    # 2. Test the Logger (Writing)
    print("\n[2] Pushing trace to Langfuse Cloud via Logger...")
    logger = LangfuseBrowserLogger(experiment_name="Langfuse Connection Test")
    
    task_name = "Verify Langfuse Integration (Mock)"
    model_name = "gpt-4o-mini"
    
    cost = logger.log_run(task=task_name, model_name=model_name, history=mock_history)
    print(f"-> Logger calculated cost: ${cost:.6f}")
    assert cost > 0, "Cost should be correctly calculated."
    
    # 3. Test the Reader (Reading)
    print("\n[3] Waiting for Langfuse Cloud to index the newly created trace (approx 3 seconds)...")
    import time
    time.sleep(3)
    print("    Fetching traces via Langfuse Reader...")
    reader = LangfuseReader(experiment_name="Langfuse Connection Test")
    
    history_records = reader.get_history(limit=5)
    
    print(f"-> Reader fetched {len(history_records)} records.")
    for idx, record in enumerate(history_records):
        print(f"   [{idx + 1}] ID: {record.run_id[:8]}... | Task: {record.task} | Cost: ${record.usage.estimated_cost_usd:.6f}")
        
    summary = reader.get_summary()
    print(f"\n-> Reader computed summary: Total Runs={summary['total_runs']}, Total Cost=${summary['total_cost_usd']:.6f}")
    
    print("\n=== Test Finalized Successfully! ===")

if __name__ == "__main__":
    test_langfuse_connection()
