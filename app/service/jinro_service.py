#이쪽은 repository


from sqlmodel import Session
from app.crud.jinro import crud_jinro
from app.models.jinro import Jinro


class JinroService:
    #db: Session 이놈은 인스턴스 메서드라서 지 자신인 self를 정의해야 한다
    def add_test_result(self, db: Session, current_user_id: int, test_result: dict, test: dict):
        
        jinro_count = len(crud_jinro.get_multi(db, current_user_id))
        version = f"v_{jinro_count + 1}.0"

        new_jinro = Jinro(
            user_id = current_user_id,
            version=version,
            test_result = test_result,
            test= test,
        )
        new_jinro = crud_jinro.create(db, jinro=new_jinro)