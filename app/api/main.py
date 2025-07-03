from fastapi import APIRouter, FastAPI
from app.api.routes.v1 import auth, jinro

app = FastAPI()

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(jinro.router, prefix="/jinro")

app.include_router(api_router, prefix="/v1") 