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

class Keyword(BaseModel):
    keyword: str
    similar_to: str
    similarity: float
    frequency: int
    

class ResumeDetailResponse(BaseModel):
    id: int
    user_id: int
    version: str
    original_filename: str | None = None
    upload_filename: str | None = None
    file_url: str | None = None
    file_path: str | None = None  # For backward compatibility
    keywords: List[Keyword]
    analysis_result: str | dict
    created_at: datetime

class ResumeListResponse(BaseModel):
    resumes: List[ResumeDetailResponse]