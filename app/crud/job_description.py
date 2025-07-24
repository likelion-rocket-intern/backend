from sqlmodel import Session, select
from typing import Optional, List
from app.models.job_description import (
    JobDescription, 
    Description, 
    TechStack, 
    JobDescriptionResult
    )
from app.schemas.job_description import (
    JobDescriptionResultCreate, 
    JobDescription as JobDescriptionSchema
    )

class CRUDJobDescription:
    def get_or_create_tech_stack(self, db: Session, *, name: str) -> TechStack:
        """
        TechStack이 존재하면 가져오고, 없으면 생성합니다.
        """
        with db.no_autoflush:
            statement = select(TechStack).where(TechStack.name == name)
            existing_tech = db.exec(statement).first()
            if existing_tech:
                return existing_tech
        
        new_tech = TechStack(name=name)
        return new_tech

    def get_or_create_description(self, db: Session, *, description: str) -> Description:
        """
        Description이 존재하면 가져오고, 없으면 생성합니다.
        """
        with db.no_autoflush:
            statement = select(Description).where(Description.description == description)
            existing_desc = db.exec(statement).first()
            if existing_desc:
                return existing_desc
            
        new_desc = Description(description=description)
        return new_desc

    def create_jd_and_result(
        self, 
        db: Session, 
        *, 
        jd_url: str,
        content: str,
        job_details: JobDescriptionSchema,
        analysis_result: JobDescriptionResultCreate,  
    ) -> JobDescription:
        """
        LLM 채용공고 분석 결과 바탕으로 JD, Description, TechStack 생성합니다.
        """
        
        # TechStack 객체
        tech_stack_objects = [
            self.get_or_create_tech_stack(db=db, name=tech_name) 
            for tech_name in job_details.tech_stacks
        ]

        # Description 객체
        description_objects = [
            self.get_or_create_description(db=db, description=desc_text)
            for desc_text in job_details.description
        ]

        # JobDescription 객체
        db_jd = JobDescription(
            jd_url=jd_url,
            content=content,
            name=job_details.name,
            tech_stacks=tech_stack_objects,
            descriptions=description_objects
        )

        # JobDescriptionResult 객체
        db_result = JobDescriptionResult(
            resume_keywords=analysis_result.resume_keywords,
            resume_strengths=[s.model_dump() for s in analysis_result.resume_strengths],
            resume_weaknesses=[w.model_dump() for w in analysis_result.resume_weaknesses],
            overall_assessment=analysis_result.overall_assessment.model_dump(),
        )

        db_jd.result = db_result

        db.add(db_jd)
        db.commit()
        db.refresh(db_jd)
        return db_jd
    
    def get_jd_by_id(self, db: Session, *, id: int) -> Optional[JobDescription]:
        """ID로 JobDescription을 조회한다."""
        return db.get(JobDescription, id)
    
    def get_result_by_id(self, db: Session, *, id: int) -> Optional[JobDescriptionResult]:
        """ID로 JobDescriptionResult를 조회한다."""
        return db.get(JobDescriptionResult, id)
    
    def get_result_by_jd_id(self, db: Session, *, job_description_id: int) -> Optional[JobDescriptionResult]:
        """JobDescription ID로 JobDescriptionResult를 조회한다."""
        statement = select(JobDescriptionResult).where(JobDescriptionResult.job_description_id == job_description_id)
        return db.exec(statement).first()

job_description_crud = CRUDJobDescription()