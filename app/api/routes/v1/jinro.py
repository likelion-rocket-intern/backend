from fastapi import APIRouter
import httpx

router = APIRouter(tags=["jinro"])

@router.get("/")
async def get_jinro():
    return {"message": "Hello, Jinro!"}

# 진로심리검사 목록 요청 (비동기)
@router.get("/tests")
async def get_psychological_tests():
    api_key = "878211ba94ee6b8314869638fe245b6a"  # 실제 발급받은 API 키 사용
    url = "https://www.career.go.kr/inspct/openapi/v2/tests"
    params = {"apikey": api_key}
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

# 입력한 값으로 문항 요청
# 커리어넷 심리검사 문항 요청 
@router.get("/test-questions")
async def get_test_questions():

    apikey = "878211ba94ee6b8314869638fe245b6a"
    q = "33"
    url = "https://www.career.go.kr/inspct/openapi/v2/test"
    params = {
        "apikey": apikey,
        "q": q
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

# 상태 요청(메인 페이지)

# 워크24 심리검사-직업코드 매핑 API 요청 (비동기)
@router.get("/work24-mapping")
async def get_work24_mapping(authKey: str, psyExamCd: str, jobsIcd: str):
    """
    워크24 심리검사-직업코드 매핑 API 요청
    - authKey: 인증키 (필수)
    - psyExamCd: 심리검사코드 (필수)
    - jobsIcd: 심리검사 직업코드 (필수)
    """
    url = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo214D02.do"
    params = {
        "authKey": authKey,
        "returnType": "JSON",
        "psyExamCd": psyExamCd,
        "jobsIcd": jobsIcd
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception:
            return {"error": "JSON 파싱 실패", "raw": response.text}
    else:
        return {
            "error": "API 요청 실패",
            "status_code": response.status_code,
            "detail": response.text
        }


