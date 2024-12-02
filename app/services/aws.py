from fastapi import UploadFile
import boto3
import uuid
from app.core.config import AWS_DEFAULT_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=AWS_DEFAULT_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.bucket = S3_BUCKET

    async def upload_file(self, file: UploadFile, key: str = None) -> str:
        try:
            # If no key is provided, generate a unique filename
            if key is None:
                file_extension = file.filename.split('.')[-1]
                key = f"{uuid.uuid4()}.{file_extension}"
            
            # Read file content
            contents = await file.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=contents,
                ContentType=file.content_type
            )
            
            # Generate URL
            url = f"https://{self.bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{key}"
            return url
            
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
        finally:
            # Reset file pointer for potential reuse
            await file.seek(0)
