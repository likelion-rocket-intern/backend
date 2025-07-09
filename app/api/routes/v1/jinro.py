from fastapi import APIRouter
import httpx
from fastapi import status
from pydantic import BaseModel, Field

from app.api.deps import SessionDep, CurrentUser
from app.service.jinro_service import JinroService
from app.core.config import settings
from app.schemas.jinro import JinroTestReportRequest

router = APIRouter(tags=["jinro"])

@router.get("/")
async def get_jinro():
    return {"message": "Hello, Jinro!"}

# 상태 요청(메인 페이지)

# 커리어넷 v1 심리검사 문항 요청 (비동기)
@router.get("/test-questions-v1")
async def get_test_questions_v1(current_user:CurrentUser):

    url = "https://www.career.go.kr/inspct/openapi/test/questions"
    params = {
        "apikey": settings.JINRO_API_KEY,
        "q": "6"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    if response.status_code == 200:
        # 여기서 유저의 정보를 받자
        current_user_id = current_user.id
        # JinroService의 save_test_redis 호출
        JinroService().save_test_redis(current_user_id, response.json())
        # 그리고 유저의 정보와 함께 
        return response.json()
    else:
        return {
            "error": "API 요청 실패",
            "status_code": response.status_code,
            "detail": response.text
        }

# 검사 결과 요청 (비동기)
@router.post("/test-report-v1")
async def post_test_report_v1(body: JinroTestReportRequest):
    url = "https://www.career.go.kr/inspct/openapi/test/report"
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body.dict(), headers=headers)
    #url2 = "https://www.career.go.kr/cloud/api/inspect/report?seq=Nzc3NzQzMDU"
    #async with httpx.AsyncClient() as client:



    if response.status_code == 200:
        # TODO 여기서 json에 있는 url를 긁어 와서 원하는 정보를 넣어둔다
           # 일단 여기서 처리하고 추후 Service에 넣을지 지켜봅시다
        # TODO 그리고 그 정보를 serviec에 저장시킨다
        return response.json()
    else:
        return {
            "error": "API 요청 실패",
            "status_code": response.status_code,
            "detail": response.text
        }

# 대충 결과 받는 api

