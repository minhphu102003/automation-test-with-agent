from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class IStorageService(ABC):
    """Interface for object storage services (S3, MinIO, etc.)."""
    
    @abstractmethod
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: str = "image/png"
    ) -> str:
        """
        Uploads a file and returns the public or signed URL.
        
        Args:
            file_content: The bytes of the file.
            filename: The destination filename in the bucket.
            content_type: The MIME type of the file.
            
        Returns:
            The URL to access the uploaded file.
        """
        pass

    @abstractmethod
    async def ensure_bucket_exists(self) -> None:
        """Ensures the target bucket exists and is properly configured."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Closes the underlying storage session."""
        pass
