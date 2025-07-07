from typing import Any
from sqlmodel import Session, select
from app.models.user import User


class CRUDUser:
<<<<<<< HEAD
    def get(self, db: Session, *, id: int) -> User | None:
        return db.exec(
            select(User).where(User.id == id)
        ).first()

    def get_by_social_info(self, db: Session, *, social_type: str, social_id: str) -> User | None:
        return db.exec(
            select(User).where(User.social_type == social_type, User.social_id == social_id)
=======
    def get_by_social_id(self, db: Session, *, social_id: str) -> User | None:
        return db.exec(
            select(User).where(User.social_id == social_id)
>>>>>>> feature/ai-backup
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

<<<<<<< HEAD
user_crud = CRUDUser()
=======
user = CRUDUser()
>>>>>>> feature/ai-backup


