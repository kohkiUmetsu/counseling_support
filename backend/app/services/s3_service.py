import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional, Iterator
import uuid
from datetime import datetime
from app.core.config import settings
import io

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_audio_file(
        self,
        file: BinaryIO,
        file_name: str,
        content_type: str,
        session_id: str
    ) -> str:
        """
        Upload audio file to S3
        Returns the S3 URL of the uploaded file
        """
        # Generate unique file name with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = file_name.split('.')[-1] if '.' in file_name else 'webm'
        s3_key = f"audio_files/{session_id}/{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        try:
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'session_id': session_id,
                        'original_filename': file_name,
                        'upload_timestamp': timestamp
                    }
                }
            )
            
            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            return file_url
            
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    def delete_audio_file(self, file_url: str) -> bool:
        """
        Delete audio file from S3
        """
        try:
            # Extract S3 key from URL
            s3_key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError as e:
            print(f"Failed to delete file from S3: {str(e)}")
            return False

    def get_presigned_url(self, file_url: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to the file
        """
        try:
            # Extract S3 key from URL
            s3_key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return presigned_url
            
        except ClientError as e:
            print(f"Failed to generate presigned URL: {str(e)}")
            return None

    def get_audio_file_stream(self, file_url: str) -> Iterator[bytes]:
        """
        Stream audio file from S3
        """
        try:
            # Extract S3 key from URL
            s3_key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            
            # Get object from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Stream the file content
            for chunk in response['Body'].iter_chunks(chunk_size=8192):
                yield chunk
                
        except ClientError as e:
            raise Exception(f"Failed to stream file from S3: {str(e)}")

s3_service = S3Service()