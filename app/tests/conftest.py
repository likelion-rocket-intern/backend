from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base # 모델 정의에 사용될 Base
from sqlalchemy import Column, Integer, String


from app.core.config import settings
from app.core.db import engine
from app.main import app
from app.models import User, Jinro
from app.models.jinro_result import JinroResult
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers



DATABASE_URL = "sqlite:///./test.db" # 테스트용 데이터베이스 파일 (인메모리 DB도 가능)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # 모델 정의 시 사용

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# JinroResult, Jinro, User, Item 모델 예시 (실제 모델 정의로 대체하세요)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Jinro(Base):
    __tablename__ = "jinro"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String)

class JinroResult(Base):
    __tablename__ = "jinro_results"
    id = Column(Integer, primary_key=True, index=True)
    result = Column(String)

# @pytest.fixture(scope="session", autouse=True)
# def db() -> Generator[Session, None, None]:
#     with Session(engine) as session:
#         yield session
#        #statement = delete(Item)
#        #session.execute(statement)
#         session = delete(JinroResult)
#         session.execute(statement)
#         session = delete(Jinro)
#         session.execute(statement)
#         statement = delete(User)
#         session.execute(statement)
#         session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )

# 기존 데이터를 보존하기 위하여 테스트로 쓰인 것들은 다 롤백시킨다
# 하지만 함수 하나 쓸때마다 죄다 롤백됨
@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()