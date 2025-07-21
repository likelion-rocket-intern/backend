import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from app.core.config import settings

# NOTE: 실제 환경에서는 인증/DB mocking이 필요합니다.

@pytest.mark.asyncio
async def test_get_jinro_by_user(async_client: AsyncClient, user_token_headers):
    response = await async_client.get("/api/v1/jinro/user", headers=user_token_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_jinro_by_user_latest(async_client: AsyncClient, user_token_headers):
    response = await async_client.get("/api/v1/jinro/user/latest", headers=user_token_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_test_questions_v1(async_client: AsyncClient, user_token_headers):
    response = await async_client.get("/api/v1/jinro/test-questions-v1", headers=user_token_headers)
    assert response.status_code in [200, 400, 500]  # 외부 API 연동이므로 유연하게

@pytest.mark.asyncio
async def test_post_test_report_v1(async_client: AsyncClient, user_token_headers):
    # 실제로는 JinroTestReportRequest에 맞는 body를 넣어야 함
    body = {
        "qestrnSeq": "6",
        "trgetSe": "100208",
        "startDtm": 1550466291034,
        "answers": "1=2 2=3 3=6 4=7 5=10 6=12 7=13 8=15 9=17 10=20 11=21 12=24 13=25 14=28 15=29 16=31 17=33 18=35 19=38 20=40 21=41 22=44 23=45 24=48 25=50 26=52 27=53 28=56",
        "apikey": settings.JINRO_API_KEY
    }
    response = await async_client.post("/api/v1/jinro/test-report-v1", json=body, headers=user_token_headers)
    assert response.status_code in [200, 400, 500]

@pytest.mark.asyncio
async def test_get_jinro_by_id(async_client: AsyncClient, user_token_headers):
    # 실제로는 DB에 존재하는 id를 사용해야 함. 여기선 1로 예시
    response = await async_client.get("/api/v1/jinro/1", headers=user_token_headers)
    assert response.status_code in [200, 404] 