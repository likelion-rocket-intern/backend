from sqlmodel import Session, select
from app.crud.jinro import crud_jinro
from app.models.jinro_result import JinroResult
from typing import Optional, List

class CRUDJinroResult:
    def create(
        self,
        db: Session,
        *,
        jinro_result: JinroResult
    ) -> JinroResult:
        db.add(jinro_result)
        db.commit()
        db.refresh(jinro_result)
        return jinro_result

    # 특정 id로 결과를 반환
    def get_by_id(self, db: Session, id: int) -> Optional[JinroResult]:
        return db.get(JinroResult, id)

    # 특정 진로 id에 대한 모든 결과를 가져옴
    def get_by_jinro_id(self, db: Session, jinro_id: int) -> List[JinroResult]:
        query = select(JinroResult)
        query = query.where(JinroResult.jinro_id == jinro_id)
        return list(db.exec(query).all())
    
    # 특정 진로 id에 대한 채신 버전을 반환
    def get_latest_by_jinro_id(self, db: Session, jinro_id: int) -> Optional[JinroResult]:
        query = select(JinroResult).where(JinroResult.jinro_id == jinro_id).order_by(JinroResult.version.desc()).limit(1)
        return db.exec(query).first()

crud_jinro_result = CRUDJinroResult()