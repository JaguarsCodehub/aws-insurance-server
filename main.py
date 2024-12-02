from dotenv import load_dotenv
import os

# Load environment variables at the very start
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from mangum import Mangum


app = FastAPI(title="Car Insurance API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Car Insurance API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }
# This is important for Vercel serverless function support
handler = Mangum(app)