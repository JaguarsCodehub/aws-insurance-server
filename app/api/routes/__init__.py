from fastapi import APIRouter
from .auth import router as auth_router
from .quotes import router as quotes_router
from .uploads import router as uploads_router
from .analysis import router as analysis_router
api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(quotes_router, prefix="/quotes", tags=["Quotes"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["Uploads"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
