from app.core.config import settings
import boto3
from typing import BinaryIO, Optional
import tempfile
import os

# Initialize S3 client once at module level
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.NCP_ACCESS_KEY,
    aws_secret_access_key=settings.NCP_SECRET_KEY,
    region_name=settings.NCP_REGION,
    endpoint_url=settings.NCP_ENDPOINT,
)

def upload_resume(file: BinaryIO, filename: str) -> Optional[str]:
    try:
        s3_client.upload_fileobj(
            file,
            settings.NCP_BUCKET_NAME,
            filename,
            ExtraArgs={
                'ContentType': 'application/pdf',
                'CacheControl': 'max-age=31536000'  # 1년 캐시
            }
        )
        # NCP Object Storage의 URL 형식
        file_url = f"https://{settings.NCP_BUCKET_NAME}.{settings.NCP_REGION}.ncloudstorage.com/{filename}"
        return file_url
    except Exception as e:
        print(f"Unexpected error during file upload: {e}")
        return None

def download_resume(filename: str) -> Optional[str]:
    try:
        # 임시 파일 생성
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        print(f"Created temporary file at: {temp_file.name}")
        
        # S3에서 파일 다운로드
        s3_client.download_file(
            settings.NCP_BUCKET_NAME,
            filename,
            temp_file.name
        )
        
        return temp_file.name
    except Exception as e:
        print(f"Error downloading file from storage: {e}")
        # 에러 발생시 임시 파일 삭제
        if 'temp_file' in locals() and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None

        #     url = s3_client.generate_presigned_url(
        #     'get_object',
        #     Params={
        #         'Bucket': settings.NCP_BUCKET_NAME,
        #         'Key': filename
        #     },
        #     ExpiresIn=7*24*60*60  # 7 days in seconds
        # )

def delete_resume(filename: str) -> None:
    try:
        filename = filename.split('/')[-1]
        s3_client.delete_object(
            Bucket=settings.NCP_BUCKET_NAME,
            Key=filename
        )
    except Exception as e:
        print(f"Error deleting file from storage: {e}")
        return None