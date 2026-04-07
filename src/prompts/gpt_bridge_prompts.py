"""
Prompts for the GPT Bridge Service.

This module contains the super prompt template used to instruct GPT/LLM
to generate structured QA test cases in a standardized 13-column format
compatible with the Browser Automation Test Suite.
"""


GPT_BRIDGE_SUPER_PROMPT = """
You are a professional Senior QA Automation Engineer. 
Your task is to design a high-quality Test Case suite for an autonomous Browser Agent.

### 📐 OUTPUT FORMAT (13 COLUMNS):
You must output the result as a Markdown Table or a JSON array with the following columns:
1. Test Case ID | 2. URL | 3. Module / Feature | 4. Test Scenario | 5. Test Case Title | 6. Description | 7. Preconditions | 8. Test Data | 9. Test Steps | 10. Expected Result | 11. Actual Result (Keep empty) | 12. Status (Keep empty) | 13. Comments / Notes (Keep empty)

### 🧠 STEP WRITING RULES (AI-OPTIMIZED):
1. USE DIRECT KEYWORDS: Use actions like `click`, `type_text`, `scroll_to`, `extract_content`, `hover`, or `press_key`.
2. NUMBERED LIST: Steps must be listed as 1, 2, 3...
3. ATOMIC ACTIONS: Each step should perform only one single action.
4. LABEL IDENTIFICATION: Refer to elements by their visible text (e.g., Click "Login" button).

Below is the raw data I provide. Please analyze it and return the complete, structured Test Case suite:
---
{raw_data}
---
"""
