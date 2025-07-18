from pydantic import BaseModel
from typing import Dict, Any, Optional

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