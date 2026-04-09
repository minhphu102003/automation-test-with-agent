import aioboto3
import logging
from typing import Optional
from src.domain.interfaces.storage import IStorageService
from src.infrastructure.config.loader import settings

logger = logging.getLogger(__name__)

class MinioStorageAdapter(IStorageService):
    def __init__(self):
        self.conf = settings.storage
        self.session = aioboto3.Session()
        self._bucket_ensured = False

    def _get_client_args(self):
        args = {
            "service_name": "s3",
            "region_name": self.conf.region,
            "aws_access_key_id": self.conf.access_key,
            "aws_secret_access_key": self.conf.secret_key,
        }
        if self.conf.endpoint_url:
            args["endpoint_url"] = self.conf.endpoint_url
        return args

    async def ensure_bucket_exists(self) -> None:
        """Helper to create bucket if missing."""
        if self._bucket_ensured:
            return

        async with self.session.client(**self._get_client_args()) as s3:
            try:
                await s3.head_bucket(Bucket=self.conf.bucket_name)
                self._bucket_ensured = True
            except Exception:
                logger.info(f"Creating bucket: {self.conf.bucket_name}")
                await s3.create_bucket(Bucket=self.conf.bucket_name)
                # Set public read policy for images if a prefix is provided
                if self.conf.public_url_prefix:
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{self.conf.bucket_name}/*"
                            }
                        ]
                    }
                    import json
                    await s3.put_bucket_policy(
                        Bucket=self.conf.bucket_name,
                        Policy=json.dumps(policy)
                    )
                self._bucket_ensured = True

    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: str = "image/png"
    ) -> str:
        await self.ensure_bucket_exists()
        
        async with self.session.client(**self._get_client_args()) as s3:
            await s3.put_object(
                Bucket=self.conf.bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=content_type
            )
            
            # Return URL
            if self.conf.public_url_prefix:
                return f"{self.conf.public_url_prefix.rstrip('/')}/{filename}"
            
            # Fallback to generating a simple URL if no prefix is set
            # (Note: this assumes the host is accessible)
            return f"{self.conf.endpoint_url or 'http://localhost'}/{self.conf.bucket_name}/{filename}"
