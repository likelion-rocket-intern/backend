from fastapi import APIRouter, HTTPException
import httpx
from fastapi import status
from pydantic import BaseModel, Field
import asyncio

from app.api.deps import SessionDep, CurrentUser
from app.service.jinro_service import JinroService
from app.core.config import settings
from app.schemas.jinro import JinroTestReportRequest, JinroResponse

router = APIRouter(tags=["jinro"])


# 한 유저에 대한 모든 결과값을 조회
@router.get("/user")
async def get_jinro_by_user(db:SessionDep, current_user:CurrentUser):
    return JinroService().find_by_user_id(db, current_user.id)

# 채신 버전 결과만 조회
@router.get("/user/latest")
async def get_jinro_by_user_latest(db:SessionDep, current_user:CurrentUser):
    return JinroService().find_by_user_id_latest(db, current_user.id)


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
async def post_test_report_v1(
    body: JinroTestReportRequest, 
    current_user: CurrentUser, 
    db: SessionDep
):
    """
    1. 커리어넷에 검사 결과 요청
    2. seq 추출 후 상세 결과 요청
    3. report6.json도 함께 요청
    4. 결과를 DB에 저장
    5. 최종 결과 반환
    """
    # 1. 커리어넷 검사 결과 요청
    report_url = "https://www.career.go.kr/inspct/openapi/test/report"
    headers = {"Content-Type": "application/json"}
    body.apikey = settings.JINRO_API_KEY

    async with httpx.AsyncClient() as client:
        report_resp = await client.post(report_url, json=body.dict(), headers=headers)

    if report_resp.status_code != 200:
        return {
            "error": "API 요청 실패",
            "status_code": report_resp.status_code,
            "detail": report_resp.text
        }

    report_data = report_resp.json()
    seq_value = None
    # 2. seq 추출
    result_url = report_data.get("RESULT", {}).get("url")
    if report_data.get("SUCC_YN") == "Y" and result_url:
        if "seq=" in result_url:
            seq_value = result_url.split("seq=")[1].split("&")[0]

    # 3. seq 값이 있으면 상세 결과 및 report6.json 요청
    if seq_value:
        detail_url = f"https://www.career.go.kr/cloud/api/inspect/report?seq={seq_value}"
        report6_url = "https://www.career.go.kr/cloud/data/report6.json"
        async with httpx.AsyncClient() as client:
            detail_resp, report6_resp = await asyncio.gather(
                client.get(detail_url),
                client.get(report6_url)
            )
        if detail_resp.status_code == 200:
            result_data = detail_resp.json()
            # report6 데이터 추가
            if report6_resp.status_code == 200:
                result_data["report6_data"] = report6_resp.json()
            else:
                result_data["report6_error"] = {
                    "status_code": report6_resp.status_code,
                    "detail": report6_resp.text
                }
            # 4. 결과 DB 저장
            result_id = JinroService().add_test_result(db, current_user.id, result_data)
            # 5. 최종 결과 반환5
            return {
                "success": True,
                "result_id": result_id,
                "message": "Success"
            }
        else:
            return {
                "error": "2차 API 요청 실패",
                "status_code": detail_resp.status_code,
                "detail": detail_resp.text
            }
    # seq 값이 없으면 원본 데이터 반환
    return {    
        "error": "결고 url추출 실패",
        "status_code": 404,
        "detail": "url에서 seq를 추출하는데 실패했습니다"
        }

@router.get("/{id}", response_model=JinroResponse)
async def get_jinro(id: int, current_user:CurrentUser, db:SessionDep):
    result = JinroService().find_by_id(db,id,current_user.id)
    if result:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 id의 결과가 없습니다."
        )