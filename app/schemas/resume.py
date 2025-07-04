from pydantic import BaseModel
from datetime import datetime
from typing import List

class AnalysisResponse(BaseModel):
    message: str
    filename: str
    status: str
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict

class ResumeDetailResponse(BaseModel):
    id: int
    user_id: int
    version: str
    file_path: str
    analysis_result: str
    created_at: datetime

class ResumeListResponse(BaseModel):
    resumes: List[ResumeDetailResponse]