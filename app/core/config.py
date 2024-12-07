import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

# Cognito
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')

# S3
S3_BUCKET = os.getenv('S3_BUCKET')

# DynamoDB
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE')