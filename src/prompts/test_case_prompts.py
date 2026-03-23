from pydantic import BaseModel
from typing import Optional

class TestCaseResult(BaseModel):
    actual_result: str
    status: str # Should be "Pass" or "Fail"
    comments: Optional[str] = None

def build_agent_prompt(row: dict) -> str:
    """
    Constructs a comprehensive prompt for the AI agent based on the structured test case.
    """
    title = row.get("Test Case Title", row.get("Test Case ID", "Unnamed Test"))
    description = row.get("Description", "")
    preconditions = row.get("Preconditions", "None")
    test_data = row.get("Test Data", "None")
    steps = row.get("Test Steps", "")
    expected_result = row.get("Expected Result", "")
    
    prompt = f"""
### TEST CASE: {title}
**Objective**: {description}

**Preconditions**: 
{preconditions}

**Test Data**: 
{test_data}

**Execution steps**:
{steps}

**Expected Result**:
{expected_result}

**IMPORTANT**: 
1. Perform the steps exactly as described.
2. If any step fails or the actual result doesn't match the expected result, stop and indicate the failure.
3. Your goal is to verify if the 'Expected Result' is achieved.

**OUTPUT INSTRUCTIONS**:
You MUST provide your final answer in the structured format with these fields:
- `actual_result`: A detailed description of what happened and what you saw on the screen.
- `status`: MUST be exactly "Pass" if the expected result was met, or "Fail" if it was not.
- `comments`: Any additional notes, bugs found, or reasons for failure.
"""
    return prompt
