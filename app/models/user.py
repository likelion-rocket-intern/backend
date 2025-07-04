from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.sql import func
from typing import List

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int = Field(default=None, primary_key=True, index=True)
    social_type: str = Field(index=True)  # "kakao", "google", etc.
    social_id: str = Field(index=True)    # The ID from the social platform
    email: str | None = Field(default=None)
    nickname: str
    profile_image: str | None = Field(default=None)
    refresh_token: str | None = Field(default=None)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": func.now()}
    )

    resumes: List["Resume"] = Relationship(back_populates="user")