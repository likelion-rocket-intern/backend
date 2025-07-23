import argparse

import httpx
from sqlmodel import Session, select
from sqlmodel import create_engine
from app.backend_pre_embed import init_embedding, init_job_profiles
from app.core import security
from app.core.config import settings
from app.crud.user import user_crud
from app.models.user import User
from app.models.jinro import Jinro
from app.models.jinro_result import JinroResult
from app.models.job_profile import JobProfile
from app.schemas.auth import UserInfo
from app.schemas.jinro import JinroTestReportRequest
from app.service.jinro_service import JinroService
import random

#더미 유저 추가
# 카카오 안거치고 그냥 바로 유저 추가
def insert_dummy_users(session):
    # 새로운 유저 생성
    new_user = User(
        social_type="kakao",
        social_id="testname",
        nickname="앙기모띠",
        email="1q2w3e4r!",
        profile_image="q"
    )
    db_user = user_crud.create_from_social(session, user=new_user)

    user_info = UserInfo(
            id=db_user.id,
            social_type="kakao",
            social_id=db_user.social_id,
            nickname=db_user.nickname,
            email=db_user.email,
            profile_image=db_user.profile_image,
        )

    access_token = security.create_access_token(user_info=user_info)
    refresh_token = security.create_refresh_token(user_info=user_info)

        
    # Update refresh token in DB
    db_user.refresh_token = refresh_token
    #db_user.access_token = access_token
    session.add(db_user)
    session.commit()
    session.refresh(db_user)


# async def insert_dummy_result(
#     body: JinroTestReportRequest):
#     # 1. 커리어넷 검사 결과 요청
#     report_url = "https://www.career.go.kr/inspct/openapi/test/report"
#     headers = {"Content-Type": "application/json"}
#     body.apikey = settings.JINRO_API_KEY

#     async with httpx.AsyncClient() as client:
#         report_resp = await client.post(report_url, json=body.dict(), headers=headers)

#     report_data = report_resp.json()
#     seq_value = None
#     # 2. seq 추출
#     result_url = report_data.get("RESULT", {}).get("url")
#     if report_data.get("SUCC_YN") == "Y" and result_url:
#         if "seq=" in result_url:
#             seq_value = result_url.split("seq=")[1].split("&")[0]

#     # 3. seq 값이 있으면 상세 결과 요청
#     if seq_value:
#         detail_url = f"https://www.career.go.kr/cloud/api/inspect/report?seq={seq_value}"
#         async with httpx.AsyncClient() as client:
#             detail_resp = await asyncio.gather(
#                 client.get(detail_url),
#             )
#         if detail_resp[0].status_code == 200:
#             result_data = detail_resp[0].json()
#             # 4. 결과 DB 저장
            # result_id = jinro_service.add_test_result(db, current_user.id, result_data)

def insert_dummy_result(body: JinroTestReportRequest, session):
    # 1. 커리어넷 검사 결과 요청
    report_url = "https://www.career.go.kr/inspct/openapi/test/report"
    headers = {"Content-Type": "application/json"}
    body.apikey = settings.JINRO_API_KEY

    with httpx.Client() as client:
        report_resp = client.post(report_url, json=body.dict(), headers=headers)

    report_data = report_resp.json()
    seq_value = None
    # 2. seq 추출
    result_url = report_data.get("RESULT", {}).get("url")
    if report_data.get("SUCC_YN") == "Y" and result_url:
        if "seq=" in result_url:
            seq_value = result_url.split("seq=")[1].split("&")[0]

    # 3. seq 값이 있으면 상세 결과 요청
    if seq_value:
        detail_url = f"https://www.career.go.kr/cloud/api/inspect/report?seq={seq_value}"
        with httpx.Client() as client:
            # asyncio.gather is not needed for a single synchronous call
            detail_resp = client.get(detail_url)

        if detail_resp.status_code == 200:
            result_data = detail_resp.json()
            # 4. 결과 DB 저장
            JinroService().add_test_result(session, 1, result_data)

# 더미 진로 추가
def insert_dummy_jinro(session, count):

    for i in range(count):
        req = JinroTestReportRequest(
            qestrnSeq="6",
            trgetSe="10028",
            startDtm=1550466291034,
            answers="1=2 2=3 3=6 4=7 5=10 6=12 7=13 8=15 9=17 10=20 11=21 12=24 13=25 14=28 15=29 16=31 17=33 18=35 19=38 20=40 21=41 22=44 23=45 24=48 25=50 26=52 27=53 28=56",
            apikey= None
        )
        insert_dummy_result(req, session)


def insert_dummy_jinro_with_results(session, count):

    jinro = Jinro(
        user_id=1,
        version="v1",
        test_result={},
        test={},
    )
    session.add(jinro)
    session.commit()
    session.refresh(jinro)

    # JobProfile ID 목록 가져오기 (SQLModel 방식)

    
    # 여기서 session.exec()를 사용해야 합니다.
    job_profile_ids = [job for job in session.exec(select(JobProfile.id)).all()] 
    
    if not job_profile_ids:
        print("Warning: No job profiles found. Cannot insert jinro_result data.")
        return

    for i in range(count):
        selected_first_job_id = random.choice(job_profile_ids)
        selected_second_job_id = random.choice(job_profile_ids)
        selected_third_job_id = random.choice(job_profile_ids)


    for i in range(count):
        result = JinroResult(
            jinro_id=jinro.id,
            version=i,
            stability_score=10,
            creativity_score=10,
            social_service_score=10,
            ability_development_score=10,
            conservatism_score=10,
            social_recognition_score=10,
            autonomy_score=10,
            self_improvement_score=10,
            first_job_id=selected_first_job_id,
            first_job_score=90.0,
            second_job_id=selected_second_job_id,
            second_job_score=80.0,
            third_job_id=selected_third_job_id,
            third_job_score=70.0,
        )
        session.add(result)
    # 루프 끝내고 한방에 커밋
    session.commit()

# # 더미 이력서 추가
# def insert_dummy_resume(session, count):
#     for i in range(count):
#         session.add(resume.ResumeModel(필드=값...))
#     session.commit()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-url', required=True)
    parser.add_argument('--count', type=int, default=100)
    args = parser.parse_args()

    # 동적으로 엔진과 세션 생성
    engine = create_engine(args.db_url)
    with Session(engine) as session: # <--- 이렇게 세션을 엽니다.
        # init_embedding(engine)
        init_job_profiles(session) # <--- 여기에 session 객체를 전달
        print("DB 연결 성공")
        insert_dummy_users(session)
        insert_dummy_jinro_with_results(session, args.count)



   # insert_dummy_resume(session, args.count)