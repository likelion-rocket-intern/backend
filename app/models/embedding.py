from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func

class Embedding(SQLModel, table=True):
	__tablename__ = "embeddings"

	id: int = Field(default=None, primary_key=True, index=True)
	object_id: int = Field(index=True)
	object_type: str = Field(index=True)
	embedding: Optional[list[float]] = Field(sa_column=Column(Vector(1536)))
	name: Optional[str] = None
	skill: Optional[str] = None
	attribute: Optional[str] = None
	description: Optional[str] = None
	created_at: datetime = Field(
		default_factory=func.now,
		sa_column_kwargs={"server_default": func.now()}
	)
	updated_at: datetime = Field(
		default=None,
		sa_column_kwargs={"onupdate": func.now()}
	)