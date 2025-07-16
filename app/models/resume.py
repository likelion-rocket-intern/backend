from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

if TYPE_CHECKING:
    from .user import User

class Resume(SQLModel, table=True):
    __tablename__ = "resumes"

    id: int = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    version: str
    file_url: str
    upload_filename: str
    original_filename: str
    analysis_result: dict | None = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    user: Optional["User"] = Relationship(back_populates="resumes")
    resume_embeddings: List["ResumeEmbedding"] = Relationship(
        back_populates="resume",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    resume_keywords: List["ResumeKeyword"] = Relationship(
        back_populates="resume",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class ResumeKeyword(SQLModel, table=True):
    __tablename__ = "resume_keywords"

    id: int = Field(default=None, primary_key=True, index=True)
    resume_id: int = Field(foreign_key="resumes.id", index=True)
    keyword: str
    similar_to: str
    similarity: float
    frequency: int
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )

    resume: Optional["Resume"] = Relationship(back_populates="resume_keywords")

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