from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING, Dict, Any
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .user import User

class Jinro(SQLModel, table=True):
    __tablename__ = "jinro"

    id: int = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    # 버전 -> 이것도 어차피 결과 테이블이 버전 역할도 해주지 않을까 싶었지만 테스트 자체가 달라질 수 있으니 그때 보류
    version: str
    # 결과 -> 이제 결과를 따로 빼게 되는데 굳이 필요할까
    test_result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    # 문제
    test: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetimㄴe = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="jinros")
    jinro_results: List["JinroResult"] = Relationship(back_populates="jinro")
