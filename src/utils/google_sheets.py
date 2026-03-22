import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import os

class GoogleSheetsClient:
    """Utility to interact with Google Sheets for data-driven testing."""
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.client = None

    def connect(self):
        """Authenticate and connect to Google Sheets API using service_account."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found at {self.credentials_path}. "
                "Please ensure it is in the root directory and named correctly."
            )
        
        # Use gspread's simplified service_account method
        self.client = gspread.service_account(filename=self.credentials_path)
        return self.client

    def get_sheet_data(self, spreadsheet_name: str, worksheet_name: str = None) -> List[Dict[str, Any]]:
        """Fetch all records from a specific worksheet."""
        if not self.client:
            self.connect()
        
        spreadsheet = self.client.open(spreadsheet_name)
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
            
        return worksheet.get_all_records()

    def update_cell(self, spreadsheet_name: str, cell: str, value: Any, worksheet_name: str = None):
        """Update a single cell in the sheet (e.g., to record test status)."""
        if not self.client:
            self.connect()
            
        spreadsheet = self.client.open(spreadsheet_name)
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
            
        worksheet.update_acell(cell, value)
