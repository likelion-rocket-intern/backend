from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

if TYPE_CHECKING:
    from .resume import Resume

class ResumeEmbedding(SQLModel, table=True):
  __tablename__ = "resume_embeddings"

  id: int = Field(default=None, primary_key=True, index=True)
  resume_id: int = Field(foreign_key="resumes.id", index=True)
  chunk_index: int
  content: str
  embedding: Optional[list[float]] = Field(sa_column=Column(Vector(1024)))
  created_at: datetime = Field(
      default_factory=func.now,
      sa_column_kwargs={"server_default": func.now()}
  )

  resume: Optional["Resume"] = Relationship(back_populates="resume_embeddings")