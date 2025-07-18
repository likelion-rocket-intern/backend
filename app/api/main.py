from fastapi import APIRouter, FastAPI
from app.api.routes.v1 import auth, crawler, jinro, resume, total, crawler

app = FastAPI()

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(resume.router, prefix="/resume")
api_router.include_router(jinro.router, prefix="/jinro")
api_router.include_router(total.router, prefix="/total")
api_router.include_router(crawler.router, prefix="/crawler")
