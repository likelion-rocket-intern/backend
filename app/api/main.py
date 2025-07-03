from fastapi import APIRouter
from app.api.routes.v1 import auth, resume

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(resume.router, prefix="/resume")

