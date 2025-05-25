import io
import uuid
from typing import Optional, Tuple

from minio import Minio
from minio.error import S3Error

from src.core.config import settings
from src.core.logger_utils import get_logger

logger = get_logger(__name__)


class MinioClient:
    _instance: Optional[Minio] = None

    def __init__(self):
        if self._instance is None:
            self._instance = Minio(
                endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=True if settings.MINIO_USE_SSL.lower() == "true" else False,
            )

    def ensure_bucket_exists(self, bucket_name: str):
        """Create bucket if it doesn't exist"""
        assert self._instance is not None
        try:
            if not self._instance.bucket_exists(bucket_name):
                self._instance.make_bucket(bucket_name)
                logger.info(f"Created bucket '{bucket_name}'")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise

    def store_document(self, content: str, bucket_name: str = "documents") -> Tuple[str, str]:
        """Store a document in MinIO and return the object ID and URI"""
        assert self._instance is not None
        try:
            self.ensure_bucket_exists(bucket_name)

            # Generate a unique object ID
            object_id = str(uuid.uuid4())

            # Convert string content to bytes
            content_bytes = content.encode("utf-8")
            content_stream = io.BytesIO(content_bytes)
            content_size = len(content_bytes)

            # Upload the document
            self._instance.put_object(
                bucket_name=bucket_name, object_name=object_id, data=content_stream, length=content_size, content_type="text/plain"
            )

            # Return both the object ID and full S3 URI
            s3_uri = f"s3://{bucket_name}/{object_id}"
            logger.info(f"Stored document as {s3_uri}")
            return object_id, s3_uri

        except S3Error as e:
            logger.error(f"Error storing document: {e}")
            raise

    def retrieve_document(self, object_id: str, bucket_name: str = "documents") -> Optional[str]:
        """Retrieve document content from MinIO"""
        assert self._instance is not None
        try:
            response = self._instance.get_object(bucket_name, object_id)
            content = response.read().decode("utf-8")
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            logger.error(f"Error retrieving document {object_id}: {e}")
            return None
