from fastapi import APIRouter
import httpx

router = APIRouter(tags=["jinro"])

@router.get("/")
async def get_jinro():
    return {"message": "Hello, Jinro!"}

# 상태 요청(메인 페이지)

# 커리어넷 v1 심리검사 문항 요청 (비동기)
@router.get("/test-questions-v1")
async def get_test_questions_v1():

    url = "https://www.career.go.kr/inspct/openapi/test/questions"
    params = {
        "apikey": "878211ba94ee6b8314869638fe245b6a",
        "q": "6"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": "API 요청 실패",
            "status_code": response.status_code,
            "detail": response.text
        }




