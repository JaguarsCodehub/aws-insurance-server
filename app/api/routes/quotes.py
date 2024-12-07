import boto3
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.utils.calculate_quote import calculate_quote
from app.services.dynamo import save_quote_to_dynamo, get_quotes_from_dynamo
import os

router = APIRouter()

# Replace the static session creation with a function that creates a fresh client
def get_dynamo_client():
    return boto3.client(
        'dynamodb',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

class QuoteRequest(BaseModel):
    carMake: str
    carModel: str
    year: int
    registrationNumber: str

class QuoteResponse(BaseModel):
    quote_id: str
    car_make: str
    car_model: str
    year: int
    registration_number: str
    premium: float

@router.post("/")
async def generate_quote(quote_request: QuoteRequest):
    try:
        print(f"Request received: {quote_request.dict()}")
        
        premium = calculate_quote(
            quote_request.carMake,
            quote_request.carModel,
            quote_request.year,
            quote_request.registrationNumber
        )
        
        print(f"Calculated premium: {premium}")
        print("Attempting to save to DynamoDB...")
        
        # Create a fresh client for each request
        dynamo_client = get_dynamo_client()
        
        quote_id = save_quote_to_dynamo(
            quote_request.carMake,
            quote_request.carModel,
            quote_request.year,
            quote_request.registrationNumber,
            premium,
        )
        
        return {
            "message": "Quote generated successfully",
            "quote_id": quote_id,
            "premium": premium
        }
    except Exception as e:
        # Enhanced error logging
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {type(e).__name__} - {str(e)}")

@router.get("/user", response_model=List[QuoteResponse])
async def get_user_quotes():
    try:
        # Get quotes from DynamoDB
        quotes = get_quotes_from_dynamo()  # We'll implement this next
        return quotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
