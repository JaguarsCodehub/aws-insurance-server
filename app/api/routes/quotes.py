from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.utils.calculate_quote import calculate_quote
from app.services.dynamo import save_quote_to_dynamo, get_quotes_from_dynamo

router = APIRouter()

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
        premium = calculate_quote(
            quote_request.carMake,
            quote_request.carModel,
            quote_request.year,
            quote_request.registrationNumber
        )
        
        quote_id = save_quote_to_dynamo(
            quote_request.carMake,
            quote_request.carModel,
            quote_request.year,
            quote_request.registrationNumber,
            premium
        )
        
        return {
            "message": "Quote generated successfully",
            "quote_id": quote_id,
            "premium": premium
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user", response_model=List[QuoteResponse])
async def get_user_quotes():
    try:
        # Get quotes from DynamoDB
        quotes = get_quotes_from_dynamo()  # We'll implement this next
        return quotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
