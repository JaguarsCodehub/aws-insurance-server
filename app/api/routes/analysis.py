from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.rekognition import RekognitionService
from app.services.aws import S3Service
from app.services.dynamo import DynamoService
import uuid
import asyncio
from app.core.config import AWS_DEFAULT_REGION

router = APIRouter()
rekognition_service = RekognitionService()
s3_service = S3Service()
dynamo_service = DynamoService()

@router.post("/analyze-car")
async def analyze_car_image(file: UploadFile = File(...)):
    try:
        # Upload file to S3
        file_extension = file.filename.split('.')[-1]
        image_key = f"car-analysis/{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3 with explicit content type
        contents = await file.read()
        s3_service.s3_client.put_object(
            Bucket=s3_service.bucket,
            Key=image_key,
            Body=contents,
            ContentType=file.content_type
        )
        
        # Wait a moment for S3 consistency
        await asyncio.sleep(1)
        
        # Get S3 URL
        s3_url = f"https://{s3_service.bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{image_key}"
        
        # Analyze with Rekognition
        try:
            analysis = rekognition_service.analyze_car_image(image_key)
        except Exception as e:
            print(f"Rekognition analysis failed: {str(e)}")
            raise

        # Store analysis results
        if analysis['damage_detected'] or analysis['confidence_score'] > 70:
            analysis_id = dynamo_service.store_analysis(s3_url, analysis)
            analysis['analysis_id'] = analysis_id
        
        return {
            "image_url": s3_url,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Full error stack: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    try:
        analysis = dynamo_service.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-license-plate")
async def detect_license_plate(file: UploadFile = File(...)):
    try:
        # Upload file to S3
        file_extension = file.filename.split('.')[-1]
        image_key = f"license-plates/{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        s3_url = await s3_service.upload_file(file, image_key)
        
        # Detect text
        text_detection = rekognition_service.detect_text_in_image(image_key)
        
        return {
            "image_url": s3_url,
            "text_detection": text_detection
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyses")
async def get_all_analyses():
    try:
        analyses = dynamo_service.get_all_analyses()  # We'll create this method
        return analyses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))