from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .resume_embedding import ResumeEmbedding
    from .user import User

class Resume(SQLModel, table=True):
  __tablename__ = "resumes"

  id: int = Field(default=None, primary_key=True, index=True)
  user_id: int = Field(foreign_key="users.id", index=True)
  version: str
  file_path: str
  analysis_result: str
  created_at: datetime = Field(
      default_factory=func.now,
      sa_column_kwargs={"server_default": func.now()}
  )
  
  user: Optional["User"] = Relationship(back_populates="resumes")
  resume_embeddings: List["ResumeEmbedding"] = Relationship(back_populates="resume")