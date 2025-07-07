from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING, Dict, Any
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .user import User

class Jinro(SQLModel, table=True):
    __tablename__ = "jinro"
    # TODO: 추후 종합 결과의 관계도 추가할것임

    id: int = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    version: str
    # json타입을 명시
    test_result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    # 근데 test가 굳이 있어야 하나? 여러 종류일지도 몰라서 그런가?
    test: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="jinros")


