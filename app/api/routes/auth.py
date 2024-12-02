from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import hmac
import base64
import hashlib

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize Cognito client
cognito_client = boto3.client(
    "cognito-idp",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

class UserAuth(BaseModel):
    email: str
    password: str

def get_secret_hash(username: str) -> str:
    msg = username + os.getenv("COGNITO_USER_POOL_CLIENT_ID")
    dig = hmac.new(
        str(os.getenv("COGNITO_CLIENT_SECRET")).encode('utf-8'), 
        msg=msg.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

@router.post("/signup")
async def sign_up(user: UserAuth):
    try:
        secret_hash = get_secret_hash(user.email)
        response = cognito_client.sign_up(
            ClientId=os.getenv("COGNITO_USER_POOL_CLIENT_ID"),
            Username=user.email,
            Password=user.password,
            SecretHash=secret_hash,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user.email
                }
            ]
        )
        
        # Auto-confirm the user (for development)
        try:
            cognito_client.admin_confirm_sign_up(
                UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                Username=user.email
            )
        except ClientError as e:
            print(f"Error in auto-confirmation: {e}")
            
        return {
            "message": "User registered successfully",
            "userSub": response["UserSub"]
        }
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user: UserAuth):
    print("Received login request:", user.dict())  # Debug print
    try:
        secret_hash = get_secret_hash(user.email)
        response = cognito_client.initiate_auth(
            ClientId=os.getenv("COGNITO_USER_POOL_CLIENT_ID"),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user.email,
                'PASSWORD': user.password,
                'SECRET_HASH': secret_hash
            }
        )
        return {
            "message": "Login successful",
            "tokens": {
                "AccessToken": response["AuthenticationResult"]["AccessToken"],
                "IdToken": response["AuthenticationResult"]["IdToken"],
                "RefreshToken": response["AuthenticationResult"]["RefreshToken"]
            }
        }
    except ClientError as e:
        print("Cognito error:", str(e))  # Debug print
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {error_message}"
        )
