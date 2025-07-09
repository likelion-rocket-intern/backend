#이쪽은 repository


from sqlmodel import Session, null
from app.crud.jinro import crud_jinro
from app.models.jinro import Jinro
import json
from app.core.redis import get_redis_client


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

    # 시험 결과와 시험 문제를 전체 저장
                # 이놈 같은 경우에는 테스트의 문항, 문제와 답변 이 2가지가 동시에 들어가야 한다
            # 그리고 문항 같은 경우에는 저장할때 json파일로 저장하든, redis에 저장하든 알아서 하면 됨
            #   그렇다면 문제 불러오기에서 어떻게든 그 문항을 저장하고
            #   결과 조회할때 나오는 api객체 안의 값을 따로 빼와서 기존 저장했던 test의 뒷편에다가 저장하면 되겠네
            #   그럼 여려명일 경우에는??
            #       그럼 그 앞에 userId를 넣어두자
            #       그리고 테스트 요청할떄 윗줄까지 해서 저장을 시킴
            #       만약 이미 그 유저 파일이 있다면 삭제하고 다시 넣음 됨
            #       혹은 그냥 여기서 그 유저 파일을 찾아서 지우면 됨
            #       혹시몰라 테스트 봤다가 나왔다가 다시 테스트 보러 들어갈지도
            #       그럼 그냥 합쳐서 요청하는 부분에서 만약 유저 아이디의 부분이 있다면 지우면 되겠네
            #       대충 파일명을 "userId_테스트"
            #    근데 생각해보면 유저가 여려명인 경우 로컬에 저장하면 우수수수 쏟아질텐데?
            #    그럼 redis에 저장하자
    def add_test_result(self, db: Session, current_user_id: int, test_result: dict):
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
        