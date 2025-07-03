from typing import Any
from sqlmodel import Session, select
from app.models.user import User


class CRUDUser:
    def get_by_social_id(self, db: Session, *, social_id: str) -> User | None:
        return db.exec(
            select(User).where(User.social_id == social_id)
        ).first()

    def create_from_social(self, db: Session, *, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_from_social(self, db: Session, *, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

user = CRUDUser()


