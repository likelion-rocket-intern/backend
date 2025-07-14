from pickletools import read_uint1
from sqlmodel import Session, select
from sqlalchemy import Column, JSON, desc
from sqlalchemy.orm import joinedload
from app.models.jinro import Jinro
from typing import Optional, List, Dict, Any
from app.models.jinro_result import JinroResult

class CRUDJinro:
    def create(
        self, 
        db: Session, 
        *,
        jinro: Jinro
    ) -> Jinro:
        db.add(jinro)
        db.commit()
        db.refresh(jinro)
        return jinro

    def get_by_id(self, db: Session, id: int) -> Optional[Jinro]:
        query = select(Jinro).where(Jinro.id == id)
        return db.exec(query).first()

    # # 한 유저id에서 모든 목록, 혹은 전원 조회
    # def get_multi(self, db: Session, user_id: Optional[int] = None) -> List[Jinro]:
    #     query = select(Jinro)
    #     if user_id is not None:
    #         query = query.where(Jinro.user_id == user_id)
    #     return list(db.exec(query).all())

    # 한 유저 id에서 모든 목록을 조회
    def get_by_userid(self, db: Session, user_id: int) -> List[Jinro]:
        query = select(Jinro)
        query = query.where(Jinro.user_id == user_id)
        return list(db.exec(query).all())
    
    def get_latest_by_user_id(self, db: Session, user_id: int) -> Optional[Jinro]:
        query = (
            select(Jinro)
            .where(Jinro.user_id == user_id)
            .order_by(desc(Jinro.version))
            .limit(1)
        )
        return db.exec(query).first()

# 인스턴스 생성
crud_jinro = CRUDJinro()

