# 🤖 GPT Web: AI-Optimized Test Case Generation Guide

To generate high-quality test cases that save tokens and maximize performance for your autonomous Browser Agent, use the **Super Prompt** below in ChatGPT (Web) or Claude.

## 🚀 How to Use

1. Copy the entire content under the **[SUPER PROMPT]** section.
2. Paste it into ChatGPT Web (GPT-4o recommended).
3. Provide your raw test requirements (e.g., "Generate 10 login and checkout test cases for Shopee").
4. Copy the resulting Table and paste it into your Excel file.

---

## 📋 [SUPER PROMPT]

```text
You are a professional Senior QA Automation Engineer. 
Your task is to design a high-quality Test Case suite for an autonomous Browser Agent.

### 📐 OUTPUT FORMAT (13 COLUMNS):
You must output the result as a Markdown Table with the following columns:
1. Test Case ID | 2. URL | 3. Module / Feature | 4. Test Scenario | 5. Test Case Title | 6. Description | 7. Preconditions | 8. Test Data | 9. Test Steps | 10. Expected Result | 11. Actual Result (Empty) | 12. Status (Empty) | 13. Comments / Notes (Empty)

### 🧠 STEP WRITING RULES (AI-OPTIMIZED):
1. USE DIRECT KEYWORDS: Use actions like `click`, `type_text`, `scroll_to`, `extract_content`, `hover`, or `press_key`.
2. NUMBERED LIST: Steps must be listed as 1, 2, 3...
3. ATOMIC ACTIONS: Each step should perform only one single action.
4. LABEL IDENTIFICATION: Refer to elements by their visible text (e.g., Click "Login" button).

### 📝 STANDARD EXAMPLE:
1. click "Login" button
2. type_text "user_test" into Username field
3. type_text "pass123" into Password field
4. click "Submit" button

Now, based on my raw description below, generate the complete Test Case suite: [ENTER YOUR REQUEST HERE]
```

---

## 💡 Quick Tips
- **Attach Documents**: If you have PRDs or API documentation (JSON), upload them along with the prompt for better accuracy.
- **Bulk Processing**: You can ask GPT to refine an entire list of rough test cases at once.
- **Formatting**: Selecting the whole table in ChatGPT and pasting it directly into Excel usually preserves all columns correctly.
