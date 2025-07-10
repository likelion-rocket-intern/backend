from pydantic import BaseModel

class TotalRequest(BaseModel):
  resume_id: int
  jinro_id: int

class TotalResponse(BaseModel):
  Strengths: str
  Weaknesses: str  