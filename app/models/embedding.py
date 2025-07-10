from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

class Embedding(SQLModel, table=True):
	__tablename__ = "embeddings"

	id: int = Field(default=None, primary_key=True, index=True)
	object_id: str = Field(index=True)
	object_type: str = Field(index=True)
	embedding: Optional[list[float]] = Field(sa_column=Column(Vector(1024)))
	extra_data: dict | None = Field(default=None, sa_column=Column(JSONB))
	created_at: datetime = Field(
		default=None,
		sa_column_kwargs={
			"server_default": func.now(), 
			"nullable": False}
	)
	updated_at: datetime = Field(
		default=None,
		sa_column_kwargs={
			"server_default": func.now(),
			"onupdate": func.now(), 
			"nullable": False}
	)