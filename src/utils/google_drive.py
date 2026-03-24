import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleDriveClient:
    """Utility to upload files to Google Drive for automation reporting."""
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/drive.file']

    def connect(self):
        """Authenticate and connect to Google Drive API."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credentials not found at {self.credentials_path}")
            
        creds = Credentials.from_service_account_file(
            self.credentials_path, 
            scopes=self.scopes
        )
        self.service = build('drive', 'v3', credentials=creds)
        return self.service

    def get_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """
        Finds a folder by name or creates it if it doesn't exist.
        """
        if not self.service:
            self.connect()
            
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        response = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])
        
        if files:
            return files[0].get('id')
        
        # Create folder if not found
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def upload_file(self, file_path: str, folder_id: str = None, custom_name: str = None) -> str:
        """
        Uploads a file to Google Drive and returns a direct webContentLink.
        """
        if not self.service:
            self.connect()
            
        file_name = custom_name or os.path.basename(file_path)
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webContentLink'
        ).execute()
        
        file_id = file.get('id')
        
        # Make the file readable by anyone with the link
        self.service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return file.get('webContentLink')
