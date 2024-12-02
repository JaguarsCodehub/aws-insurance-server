import boto3
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from app.core.config import AWS_DEFAULT_REGION, DYNAMODB_TABLE
import uuid

# Load environment variables
load_dotenv()

# Get AWS configuration from environment variables
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION') or os.getenv('AWS_REGION')

dynamo_client = boto3.resource(
    'dynamodb',
    region_name=AWS_DEFAULT_REGION,
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
table = dynamo_client.Table(DYNAMODB_TABLE)

def save_quote_to_dynamo(car_make: str, car_model: str, year: int, registration_number: str, premium: float):
    insurance_id = str(uuid.uuid4())
    table.put_item(Item={
        "insurance_id": insurance_id,
        "quote_id": str(uuid.uuid4()),
        "car_make": car_make,
        "car_model": car_model,
        "year": year,
        "registration_number": registration_number,
        "premium": Decimal(str(premium))
    })
    return insurance_id

def get_quotes_from_dynamo():
    try:
        response = table.scan()  # For now, we'll get all quotes. In production, filter by user_id
        items = response.get('Items', [])
        
        # Convert Decimal to float for JSON serialization
        for item in items:
            if 'premium' in item:
                item['premium'] = float(item['premium'])
                
        return items
    except Exception as e:
        raise Exception(f"Failed to fetch quotes: {str(e)}")

class DynamoService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('car_damage_analyses')

    def store_analysis(self, image_url: str, analysis_results: Dict[str, Any]) -> str:
        analysis_id = str(uuid.uuid4())
        
        # Convert float values to Decimal for DynamoDB
        def convert_floats(obj):
            if isinstance(obj, float):
                return Decimal(str(obj))
            elif isinstance(obj, dict):
                return {k: convert_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_floats(i) for i in obj]
            return obj

        try:
            # Convert boolean to number for the GSI
            damage_detected_num = 1 if analysis_results.get('damage_detected', False) else 0
            
            item = {
                'analysis_id': analysis_id,
                'image_url': image_url,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_results': convert_floats(analysis_results),
                'is_vehicle': analysis_results.get('is_vehicle', False),
                'damage_detected': damage_detected_num,  # Store as number
                'confidence_score': convert_floats(analysis_results.get('confidence_score', 0))
            }
            
            self.table.put_item(Item=item)
            return analysis_id
            
        except Exception as e:
            raise Exception(f"Failed to store analysis: {str(e)}")

    def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        try:
            response = self.table.get_item(Key={'analysis_id': analysis_id})
            item = response.get('Item')
            if item:
                # Convert number back to boolean for damage_detected
                item['damage_detected'] = bool(item['damage_detected'])
            return item
        except Exception as e:
            raise Exception(f"Failed to retrieve analysis: {str(e)}")

    def get_all_analyses(self):
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Convert Decimal back to float and number back to boolean
            def convert_types(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, dict):
                    result = {k: convert_types(v) for k, v in obj.items()}
                    # Convert damage_detected back to boolean at the top level
                    if 'damage_detected' in result:
                        result['damage_detected'] = bool(result['damage_detected'])
                    return result
                elif isinstance(obj, list):
                    return [convert_types(i) for i in obj]
                return obj
            
            return [convert_types(item) for item in items]
        except Exception as e:
            raise Exception(f"Failed to fetch analyses: {str(e)}")
