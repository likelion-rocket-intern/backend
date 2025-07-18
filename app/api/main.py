from fastapi import APIRouter, FastAPI
from app.api.routes.v1 import auth, jinro, resume, total

app = FastAPI()

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(resume.router, prefix="/resume")
api_router.include_router(jinro.router, prefix="/jinro")
api_router.include_router(total.router, prefix="/total")
