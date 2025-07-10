#이쪽은 repository


from sqlmodel import Session, null
from app.crud.jinro import crud_jinro
from app.models.jinro import Jinro
import json
from app.core.redis import get_redis_client
from typing import Optional, List


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


    def add_test_result(self, db: Session, current_user_id: int, test_result: dict) -> int:
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
        
        jinro_count = len(crud_jinro.get_by_userid(db, current_user_id))
        version = f"v_{jinro_count + 1}.0"

        # 결과를 저장
        new_jinro = Jinro(
            user_id = current_user_id,
            version=version,
            test_result = test_result,
            test= stored_test,
        )
        new_jinro = crud_jinro.create(db, jinro=new_jinro)
        
        # Redis에서 임시 데이터 삭제 (테스트 완료 후 정리)
        if redis_data:
            redis_client.delete(redis_key)
        
        return new_jinro.id
    
    # id 가지고 조회
    def find_by_id(self, db: Session, id: int) -> Optional[Jinro]:
        return crud_jinro.get_by_id(db, id)
    
    # 유저 아이디 가지고 조회
    def find_by_user_id(self, db: Session, id: int)-> List[Jinro]:
        return crud_jinro.get_by_userid(db, id)