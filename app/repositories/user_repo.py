from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        return self.db.scalar(stmt)

    def get_or_create(self, *, telegram_id: int, first_name: str, username: str | None = None, language: str = "en") -> User:
        user = self.get_by_telegram_id(telegram_id)
        if user is not None:
            return user
        user = User(telegram_id=telegram_id, first_name=first_name, username=username, language=language)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
