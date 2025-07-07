from sqlmodel import Session, select
from sqlalchemy import Column, JSON
from app.models.jinro import Jinro
from typing import Optional, List, Dict, Any

#obj_in는 
class CRUDJinro:
    def create(
        # self는 객체 자기자신
        self, 
        # Session는 임시방편
        db: Session, 
        # 이놈이 실제 넣을 데이터(dict타입)
        obj_in: Dict[str, Any]
    ) -> Jinro:
    # dict파일을 데이터에 넣기 편한 객체로 변환
        db_obj = Jinro(**obj_in)
        # db세션에 추가
        db.add(db_obj)
        # 트랜잭션 커밋
        db.commit() #fastAPI는 트랜잭셔널을 수동으로 적용시켜야 한다
        # db갱신
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, id: int) -> Optional[Jinro]:
        return db.get(Jinro, id)

    # 한 유저id에서 모든 목록, 혹은 전원 조회
    def get_multi(self, db: Session, user_id: Optional[int] = None) -> List[Jinro]:
        query = select(Jinro)
        if user_id is not None:
            query = query.where(Jinro.user_id == user_id)
        return list(db.exec(query).all())

    # 삭제
    def remove(self, db: Session, id: int) -> Optional[Jinro]:
        obj = db.get(Jinro, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj



