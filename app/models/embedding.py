from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

class Embedding(SQLModel, table=True):
	__tablename__ = "embeddings"

	id: int = Field(default=None, primary_key=True)
	object_id: int
	object_type: str
	embedding : list[float] = Field(
		sa_column=Column(Vector(768))
	)
	name: Optional[str] = None
	skill: Optional[str] = None
	attribute: Optional[str] = None
	description: Optional[str] = None
	created_at: datetime = Field(default_factory=datetime.utcnow)
	updated_at: datetime = Field(default_factory=datetime.utcnow)