import sys
import os

# Add the project root to sys.path so we can import our modules
sys.path.append(os.getcwd())

from src.utils.google_sheets import GoogleSheetsClient

def verify_connection():
    print("=== Google Sheets Connection Verification ===")
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json file not found in the root directory.")
        return

    client = GoogleSheetsClient()
    
    try:
        print("1. Attempting to authenticate...")
        gspread_client = client.connect()
        print("✅ Authentication successful!")
        
        print("\n2. Fetching list of accessible spreadsheets...")
        files = gspread_client.list_spreadsheet_files()
        
        if not files:
            print("⚠️ Authentication succeeded, but THE BOT CANNOT SEE ANY FILES.")
            print("👉 IMPORTANT: You MUST share your Google Sheet with the Service Account email.")
            # We can extract the email from the credentials to show the user
            import json
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                bot_email = creds.get('client_email')
                print(f"👉 Please share your sheet with: {bot_email}")
        else:
            print(f"✅ Success! The bot can see {len(files)} spreadsheet(s):")
            for i, f in enumerate(files, 1):
                print(f"   [{i}] Name: '{f['name']}' (ID: {f['id']})")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    verify_connection()
