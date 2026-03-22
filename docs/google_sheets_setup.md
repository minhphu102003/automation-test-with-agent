# Google Sheets Setup & Verification Guide

This guide explains how to connect the automation suite to Google Sheets and how to verify the connection using the built-in verification tool.

## 🔑 1. Obtaining Credentials

1.  Visit the [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable **Google Sheets API** and **Google Drive API**.
3.  Create a **Service Account** and generate a **JSON Key**.
4.  Download the JSON file, rename it to `credentials.json`, and place it in the project root.

## 🤝 2. Sharing the Sheet

The bot acts as a specific user with its own email address. You must share your Google Sheet with this email:
- Open your Google Sheet.
- Click **Share**.
- Paste the `client_email` found inside your `credentials.json`.
- Grant **Editor** permissions.

## ✅ 3. Verifying the Connection

We provide a dedicated script to test the connection and ensure the bot can "see" your files.

### Execution Command:
```powershell
uv run python tests/verify_sheets.py
```

### Understanding the Results:
- **✅ Authentication successful!**: The `credentials.json` is valid and the API is reachable.
- **⚠️ Authentication succeeded, but THE BOT CANNOT SEE ANY FILES**: This means you haven't shared the sheet with the bot yet. Follow the steps in Section 2 above.
- **✅ Success! The bot can see X spreadsheet(s)**: Everything is perfect. You are ready to run data-driven tests.

---

## 🚀 4. Running Data-Driven Tests

Once verified, you can enable data-driven testing in `main.py`:

1.  Open `main.py`.
2.  Uncomment `await run_data_driven_test("YourSheetName")`.
3.  Ensure your sheet has `task` and `model` columns (or your custom columns).
