from sqlmodel import Session, select
from sqlalchemy import Column, JSON
from app.models.jinro import Jinro
from typing import Optional, List, Dict, Any

#obj_in는 
class CRUDJinro:
    def create(
        # self는 객체 자기자신, db: Session는 인스터
        self, 
        # 얘가 db세션
        # 근데 요놈이 인스턴스 메스드인데 저걸 인자로 넣고 싶다면 저 self도 같이 넣어야 한다
        db: Session, 
        # 얘는 jinro인자를 반드시 키워드로만 받게 강제시킨다고 한다
        # 왜냐면 인자가 많아지면 실수로 순서를 바뀌게 될 수 있다고 해서
        # 호출시 이름=값 형태로 반드시 넣어야 한다고 한다
        *,
        # 이놈이 실제 넣을 데이터(dict타입)
        jinro: Jinro
    ) -> Jinro:
    # dict파일을 데이터에 넣기 편한 객체로 변환
        # db세션에 추가
        db.add(jinro)
        # 트랜잭션 커밋
        db.commit() #fastAPI는 트랜잭셔널을 수동으로 적용시켜야 한다
        # db갱신
        db.refresh(jinro)
        return jinro

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

# 인스턴스 생성
crud_jinro = CRUDJinro()

