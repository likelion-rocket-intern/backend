from sqlmodel import Session, select
from typing import Optional, List
from app.models.job_description_result import JobDescriptionAnalysisResult

class CRUDJobDescriptionAnalysisResult:
    def create(
        self,
        db: Session,
        *,
        result: JobDescriptionAnalysisResult  # 매개변수 이름을 result로 변경
    ) -> JobDescriptionAnalysisResult:
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    def get_by_id(self, db: Session, id: int) -> Optional[JobDescriptionAnalysisResult]:
        return db.get(JobDescriptionAnalysisResult, id)

    # 특정 이력서에 대한 모든 분석 결과를 가져오는 메서드
    def get_by_resume_id(self, db: Session, resume_id: int) -> List[JobDescriptionAnalysisResult]:
        query = select(JobDescriptionAnalysisResult).where(JobDescriptionAnalysisResult.resume_id == resume_id)
        return list(db.exec(query).all())


crud_job_description_analysis_result = CRUDJobDescriptionAnalysisResult()
