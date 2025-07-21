# app/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import psutil

# 기본 HTTP 메트릭
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# 시스템 메트릭
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage')

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 경로 정보
        route_path = request.url.path
        if request.scope.get('route'):
            route_path = request.scope['route'].path
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # 메트릭 기록
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=route_path,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=route_path
        ).observe(duration)
        
        return response

def update_system_metrics():
    """시스템 메트릭 업데이트"""
    process = psutil.Process()
    MEMORY_USAGE.set(process.memory_info().rss)
    CPU_USAGE.set(process.cpu_percent())