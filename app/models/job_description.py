from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, TEXT

if TYPE_CHECKING:
    from .resume import Resume  

class JobDescription(SQLModel, table=True):
    __tablename__ = "job_descriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(TEXT, nullable=False))
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

    resume_id: int = Field(foreign_key="resumes.id")
    
    resume: "Resume" = Relationship(back_populates="job_descriptions")

    result: Optional["JobDescriptionResult"] = Relationship(back_populates="job_description")
