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

    def _open_spreadsheet(self, spreadsheet_id_or_url: str):
        """Internal helper to open a spreadsheet by name or URL."""
        if not self.client:
            self.connect()
        
        if spreadsheet_id_or_url.startswith('https://'):
            return self.client.open_by_url(spreadsheet_id_or_url)
        return self.client.open(spreadsheet_id_or_url)

    def get_sheet_data(self, spreadsheet_id_or_url: str, worksheet_name: str = None) -> List[Dict[str, Any]]:
        """Fetch all records from a specific worksheet."""
        spreadsheet = self._open_spreadsheet(spreadsheet_id_or_url)
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

    def update_row_results(self, spreadsheet_id_or_url: str, test_id: str, results: Dict[str, Any], worksheet_name: str = None):
        """
        Update multiple columns for a specific test case identified by its ID.
        """
        spreadsheet = self._open_spreadsheet(spreadsheet_id_or_url)
        if worksheet_name:
            worksheet = spreadsheet.worksheet(worksheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
            
        # Get all records to find the row index
        records = worksheet.get_all_records()
        headers = worksheet.row_values(1)
        
        # Find row index (1-indexed, +1 for headers)
        row_idx = -1
        for i, row in enumerate(records):
            # Try different common ID headers if "Test Case ID" is not found
            id_val = str(row.get("Test Case ID") or row.get("ID") or "")
            if id_val == str(test_id):
                row_idx = i + 2
                break
        
        if row_idx == -1:
            print(f"Warning: Test Case ID '{test_id}' not found in sheet.")
            return

        # Update each result column
        for header, value in results.items():
            try:
                col_idx = headers.index(header) + 1
                worksheet.update_cell(row_idx, col_idx, value)
            except ValueError:
                print(f"Warning: Header '{header}' not found in sheet.")
