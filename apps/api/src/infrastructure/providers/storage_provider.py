"""File storage provider abstraction"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
import os
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageProvider(ABC):
    """Abstract storage provider interface"""

    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = "uploads"
    ) -> str:
        """Upload a file and return its URL"""
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """Delete a file"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local file storage provider"""

    def __init__(self):
        self.base_path = Path(os.getenv('UPLOAD_DIR', '/app/uploads'))
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8001')
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = "uploads"
    ) -> str:
        """Upload a file to local storage"""
        try:
            # Generate unique filename
            ext = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{ext}"

            # Create folder if not exists
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

            # Save file
            file_path = folder_path / unique_filename
            with open(file_path, 'wb') as f:
                content = file.read()
                f.write(content)

            # Return URL
            file_url = f"{self.base_url}/uploads/{folder}/{unique_filename}"
            logger.info(f"File uploaded: {file_url}")
            return file_url

        except Exception as e:
            logger.error(f"Failed to upload file {filename}: {e}")
            raise

    async def delete_file(self, file_url: str) -> bool:
        """Delete a file from local storage"""
        try:
            # Extract path from URL
            path_part = file_url.replace(self.base_url, '')
            file_path = Path(str(self.base_path.parent) + path_part)

            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_url}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete file {file_url}: {e}")
            return False


def get_storage_provider() -> StorageProvider:
    """Get configured storage provider"""
    # Can be extended to support S3, Azure Blob, etc.
    return LocalStorageProvider()
