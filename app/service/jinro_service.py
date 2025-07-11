#이쪽은 repository


from sys import version
from sqlmodel import Session, null
from app.crud import jinro
from app.crud.jinro import crud_jinro
from app.crud.jinro_result import crud_jinro_result
from app.models.jinro import Jinro
import json
from app.core.redis import get_redis_client
from typing import Optional
from app.models.jinro_result import JinroResult
from app.models.job_profile import JobProfile
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlmodel import select


class JinroService:
    #db: Session 이놈은 인스턴스 메서드라서 지 자신인 self를 정의해야 한다

    # 시험 문제를 저장, redis에 임시로 저장한다
    def save_test_redis(self, user_id: int, test: dict):
        # 임시로 저장할 dict 생성
        temp_data = {
            "user_id": user_id,
            "test": test
        }
        
        # Redis 클라이언트 가져오기
        redis_client = get_redis_client()
        
        # 키 이름 생성 (user_id를 포함하여 고유하게)
        redis_key = f"jinro_test_{user_id}"
        
        # 이미 데이터가 있다면 삭제
        # 왜냐면 정보 갱신을 위해서
        if redis_client.get(redis_key):
            redis_client.delete(redis_key)
        
        # dict를 JSON 문자열로 변환하여 Redis에 저장
        # 만료 시간을 1시간(3600초)으로 설정
        redis_client.setex(
            redis_key, 
            3600,  # 1시간 후 만료
            json.dumps(temp_data, ensure_ascii=False)
        )
        
        return redis_key

    
# 여기를 다시 만들어봅시다
# 일단 테스트를 찾고, 없으면 만들고
# 있다면 그 테스트 id를 빌려와서 결과를 저장시키기

    # 새로운 테스트가 떴으면 추가 하기
    def add_new_test(self, db:Session, current_user_id: int, test_result:dict, version: str):
        # Redis에서 저장된 데이터 가져오기
        redis_client = get_redis_client()
        redis_key = f"jinro_test_{current_user_id}"
        redis_data = redis_client.get(redis_key)
        
        # Redis에서 데이터를 가져온 경우, 저장된 test 데이터 사용
        if redis_data:
            # bytes를 문자열로 디코딩
            redis_data_str = redis_data.decode('utf-8') if isinstance(redis_data, bytes) else str(redis_data)
            temp_data = json.loads(redis_data_str)
            stored_test = temp_data.get("test")  # Redis에 저장된 test를 가져온다
        else:
            stored_test = None #여기에 예외처리를 해야 하는데

        # 결과를 저장
        new_jinro = Jinro(
            user_id = current_user_id,
            version=version,
            # 이 결과는 따로 빼놨으니 상관 없을지도
            test_result = test_result,
            test= stored_test,
        )
        new_jinro = crud_jinro.create(db, jinro=new_jinro)

        
        # Redis에서 임시 데이터 삭제 (테스트 완료 후 정리)
        if redis_data:
            redis_client.delete(redis_key)
        
        return new_jinro
    
    # 테스트 결과 추가하기

    def add_test_result(self, db: Session, current_user_id: int, test_result: dict):
        # 헤당 유저가 테스트를 치뤘다면 거기에 넣고 없다면 새로 jinro를 만들기
        # 신규 유저가 테스트를 할 경우 없으니까 만들어야지
        # 그럼 만약에 테스트 자체가 새로 바뀔 경우에는? -> 그리 되면 이후의 값들도 싹다 갈아 엎어야 해서 상관없을듯
        
        # 없으면 추가
        jinro_count = len(crud_jinro.get_by_userid(db, current_user_id))
        if jinro_count == 0:
            jinro = self.add_new_test(db, current_user_id, test_result, f"v_{jinro_count + 1}.0")
        # 있으면 채신 버전에서 가져오기
        else:
            jinro = crud_jinro.get_latest_by_user_id(db, current_user_id)
            if jinro is None:
             raise ValueError("해당 user_id에 대한 Jinro가 존재하지 않습니다.")
        
        # 이후 테스트 결과에서 원하는 값만 추출하고 넣는 부분을 진행
        scores = {f"w{i}": test_result.get(f"w{i}") for i in range(1, 9)}
        # 스코어를 float로 변환
        user_score = [float(i) if i is not None else 0.0 for i in scores.values()]

        result = self.calculate_similarity(user_score, db)

        # result = 함수호출(user_score) #-> list로 반환, 여기만 함수 호출 바꾸면 됨

        # 거기서 상위3종으로 
        top3 = result[:3]

        
        # 버전도 채신 버전에서 가져오기
        version_count = len(crud_jinro_result.get_by_jinro_id(db, jinro.id)) + 1


        jinro_result = JinroResult( # 해당 진로검사 id
            jinro_id=jinro.id,
            version=version_count,  # 필요시 version 값
            stability_score=scores["w1"] or -1,
            creativity_score=scores["w2"] or -1,
            social_service_score=scores["w3"] or -1,
            ability_development_score=scores["w4"] or -1,
            conservatism_score=scores["w5"] or -1,
            social_recognition_score=scores["w6"] or -1,
            autonomy_score=scores["w7"] or -1,
            self_improvement_score=scores["w8"] or -1,
            first_job_id=top3[0]["id"],
            first_job_score=top3[0]["percentage"],
            second_job_id=top3[1]["id"],
            second_job_score=top3[1]["percentage"],
            third_job_id=top3[2]["id"],
            third_job_score=top3[2]["percentage"]
        )
        
        # 이제 저걸 저장
        jinro_result = crud_jinro_result.create(db, jinro_result=jinro_result)

        return jinro_result.id
    
    # id 가지고 조회
    def find_by_id(self, db: Session, id: int) -> Optional[Jinro]:
        return crud_jinro.get_by_id(db, id)
    
    # 유저 아이디 가지고 결과 조회
    def find_by_user_id(self, db: Session, user_id: int)-> List[JinroResult]:
        # TODO 근데 이전 버전 테스트는 우짜지
        jinro = crud_jinro.get_latest_by_user_id(db, user_id)
        if jinro is None:
            return [] 
        return crud_jinro_result.get_by_jinro_id(db, jinro.id)
        # 여기서 스키마로 딱 바꾸면 좋은데
    

    # 유저 아이디 가지고 채신 결과 조회
    def find_by_user_id_latest(self, db: Session, user_id: int) -> Optional[JinroResult]:
        jinro = crud_jinro.get_latest_by_user_id(db, user_id)
        if jinro is None:
            return None
        return crud_jinro_result.get_latest_by_jinro_id(db, jinro.id)



    
    def calculate_similarity(self, user: List[float], session: Session) -> List[Dict]:
        # DB에서 활성화된 직군 프로필 조회
        job_profiles = session.exec(select(JobProfile).where(JobProfile.is_active == True)).all()
        
        if not job_profiles:
            return []
        
        # 사용자 벡터 (2D 배열로 변환)
        user_vector = np.array(user).reshape(1, -1)
        
        # 직군 프로필 벡터들 추출 (JobProfile 모델의 get_vector() 메서드 사용)
        job_vectors = np.array([profile.get_vector() for profile in job_profiles])
        
        # 코사인 유사도 계산
        similarities = cosine_similarity(user_vector, job_vectors).flatten()
        
        # 결과 생성
        results = []
        for i, (profile, similarity) in enumerate(zip(job_profiles, similarities)):
            result = {
                "id": profile.id,
                "job_type": profile.job_type,
                "job_name_ko": profile.job_name_ko,
                "similarity": similarity,
                "percentage": round(similarity * 100, 2),
                "rank": 0  # 정렬 후 설정
            }
            results.append(result)
        
        # 유사도 높은 순으로 정렬 및 순위 설정
        results.sort(key=lambda x: x["similarity"], reverse=True)
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        return results
