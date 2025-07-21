import sentry_sdk
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.api.main import api_router
from app.core.config import settings
from app.monitoring import PrometheusMiddleware, update_system_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,  # 설정된 모든 CORS 오리진 허용
    allow_credentials=True,                   # 쿠키 허용
    allow_methods=["*"],                      # 모든 HTTP 메서드 허용
    allow_headers=["*"],                      # 모든 헤더 허용
)

app.add_middleware(PrometheusMiddleware)

@app.get("/metrics", tags=["system"])
async def metrics():
    update_system_metrics()
    return JSONResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix=settings.API_V1_STR)
