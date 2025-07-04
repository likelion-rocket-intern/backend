from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    message: str
    filename: str
    status: str
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict