from pydantic import BaseModel, Field as PydanticField
from typing import Dict, Any, Optional, List

class JobDescriptionRequest(BaseModel):
    content: str

class JobDescriptionResultResponse(BaseModel):
    analysis_result: Dict[str, Any] 

class JobAnalysisTaskResponse(BaseModel):
    task_id: str
    message: str

class JobTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

class JobSummarySchema(BaseModel):
    name: str
    skill: List[str]

class OverallAssessmentSchema(BaseModel):
    score: int
    summary: str

class ResumeStrengthSchema(BaseModel):
    keyword: str
    evidence: str

class ResumeWeaknessSchema(BaseModel):
    keyword: str
    evidence: str

class JobDescriptionResultBase(BaseModel):
    job_summary: JobSummarySchema
    overall_assessment: OverallAssessmentSchema
    job_keywords: List[str]
    resume_keywords: List[str]
    resume_strengths: List[ResumeStrengthSchema]
    resume_weaknesses: List[ResumeWeaknessSchema]

class JobDescriptionResultCreate(JobDescriptionResultBase):
    pass

class JobDescriptionResultResponse(JobDescriptionResultBase):
    id: int
    job_description_id: int
    created_at: str