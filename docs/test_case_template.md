# Google Sheet Test Case Template Guide

This document describes the required structure for the Google Sheet used in the automated browser testing suite. To ensure the AI Agent can correctly execute tests and report results, follow these column definitions.

## 📊 Required Column Headers

Your Google Sheet **MUST** include the following headers in the first row (case-sensitive):

| Column Header | Description | Required | Example |
| :--- | :--- | :---: | :--- |
| **Test Case ID** | A unique identifier for the test case. | Yes | `TC-001` |
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

### 1. Test Steps (Be Explicit)
The AI Agent follows your steps literal. Use clear, numbered steps.
- **Good:** `1. Click the "Login" button. 2. Enter "admin" in the username field.`
- **Bad:** `Login to the app.`

### 2. Test Data
If you have multiple inputs, list them clearly. The Agent is good at extracting values from natural text or JSON.
- **Example:** `Username: admin_user | Password: secret_password`

### 3. Agent Metadata
You can also add a `model` column if you want to specify which LLM (e.g., `gpt-4o`, `gemini-1.5-pro`) to use for a specific test case.

## 🚀 How to Run
1. Share your sheet with the Service Account email.
2. Update `.env` with `TEST_SPREADSHEET_NAME`.
3. Run `python -m tests.structured_test_runner`.
