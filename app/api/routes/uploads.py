from fastapi import APIRouter, UploadFile, HTTPException
from app.services.aws import S3Service

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile):
    try:
        s3_service = S3Service()
        url = s3_service.upload_file(file)
        return {"message": "File uploaded successfully", "file_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
