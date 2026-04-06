# Google Sheet Test Case Template Guide

This document describes the required structure for the Google Sheet used in the automated browser testing suite. To ensure the AI Agent can correctly execute tests and report results, follow these column definitions.

## 📊 Required Column Headers

Your Google Sheet **MUST** include the following headers in the first row (case-sensitive):

| Column Header | Description | Required | Example |
| :--- | :--- | :---: | :--- |
| **Test Case ID** | A unique identifier for the test case. | Yes | `TC-001` |
| **URL** | The target URL for this specific test case. | No | `https://example.com/login` |
| **Module / Feature** | The name of the module or feature being tested. | No | `Login`, `Checkout` |
| **Test Scenario** | High-level goal of the test. | No | `Verify login with valid credentials` |
| **Test Case Title** | The title of the test case. | Yes | `Successful Login` |
| **Description** | Detailed description of the test objective. | Yes | `User should be able to login to the system.` |
| **Preconditions** | Conditions that must be met before starting the test. | Yes | `User is on the login page` |
| **Test Data** | Input data required for the test (JSON format recommended). | Yes | `{"user": "admin", "pass": "123"}` |
| **Test Steps** | Step-by-step instructions for the AI Agent. | Yes | `1. Enter user\n2. Enter pass\n3. Click Login` |
| **Expected Result** | What should happen if the test passes. | Yes | `Redirect to Dashboard` |
| **Actual Result** | **(Leave Empty)** - Filled automatically by Agent. | - | - |
| **Status (Pass/Fail)**| **(Leave Empty)** - Filled automatically by Agent. | - | - |
| **Evidence** | **(Leave Empty)** - Path to proof screenshot. | - | - |
| **Priority** | Importance: High, Medium, or Low. | No | `High` |
| **Comments / Notes** | **(Leave Empty)** - Filled automatically by Agent. | - | - |

## 💡 Best Practices for Writing Test Cases

### 1. Test Steps (AI-Optimized Guidance)

To save tokens and ensure the Agent follows your plan strictly (Guided Planning), use **Direct Action Verbs** and **Numbered Lists**.

#### ✅ Best Practices:
- **Use Direct Keywords**: Refer to actions like `click`, `type_text`, `scroll_to`, `extract`, `hover`, or `press_key`.
- **One Action per Step**: Keep steps simple and atomic.
- **Refer to Elements by Label**: Use visible text on buttons (e.g., `Click "Add to Cart"` instead of `Click the green button`).

#### ❌ Avoid:
- Vague goals like "Try to buy something".
- Compound steps like "Log in and then find the shoes and then buy them".

#### 🔄 Example (Before vs. After):
- **Bad**: `Go to login and enter credentials.`
- **Good**:
  1. `Click "Sign In" button`
  2. `type_text "admin" into Username field` (Use data from **Test Data** column)
  3. `type_text "pass123" into Password field`
  4. `Click "Submit" button`

### 2. Test Data (Contextual Integration)

The Agent can extract values from this column automatically. You can provide JSON or a simple list.
- **Recommended Format**: `{"username": "admin", "password": "secret"}`
- **In Steps**: You can refer to them like `type_text the password from Test Data into the Password input`.

### 3. Agent Metadata
You can also add a `model` column if you want to specify which LLM (e.g., `gpt-4o`, `gemini-1.5-pro`) to use for a specific test case.

## 🚀 How to Run
1. Share your sheet with the Service Account email.
2. Update `.env` with `TEST_SPREADSHEET_NAME`.
3. Run `python -m tests.structured_test_runner`.
