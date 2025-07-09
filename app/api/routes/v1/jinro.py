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
async def post_test_report_v1(body: JinroTestReportRequest, current_user:CurrentUser, db: SessionDep):
    url = "https://www.career.go.kr/inspct/openapi/test/report"
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body.dict(), headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        # url에서 seq 파라미터 값 추출
        seq_value = None
        if response_data.get("SUCC_YN") == "Y" and response_data.get("RESULT", {}).get("url"):
            url = response_data["RESULT"]["url"]
            if "seq=" in url:
                seq_value = url.split("seq=")[1]
                if "&" in seq_value:
                    seq_value = seq_value.split("&")[0]
        # seq 값이 있으면 새로운 API에 요청
        if seq_value:
            url2 = f"https://www.career.go.kr/cloud/api/inspect/report?seq={seq_value}"
            async with httpx.AsyncClient() as client:
                response2 = await client.get(url2)
            if response2.status_code == 200:
                # report6.json API도 함께 요청
                url3 = "https://www.career.go.kr/cloud/data/report6.json"
                async with httpx.AsyncClient() as client:
                    response3 = await client.get(url3)
                
                result_data = response2.json()
                if response3.status_code == 200:
                    result_data["report6_data"] = response3.json()
                else:
                    result_data["report6_error"] = {
                        "status_code": response3.status_code,
                        "detail": response3.text
                    }
                    JinroService().add_test_result(db, current_user.id, result_data) 
                
                return result_data
            else:
                return {
                    "error": "2차 API 요청 실패",
                    "status_code": response2.status_code,
                    "detail": response2.text
                }
        # seq 값이 없으면 기존 데이터 리턴
        return response_data
    else:
        return {
            "error": "API 요청 실패",
            "status_code": response.status_code,
            "detail": response.text
        }

# 대충 결과 받는 api

