from __future__ import annotations

from app.models.content import Content
from app.repositories.user_repo import UserRepository
from app.utils.text import sanitize_text


class ConfessionService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)

    def create(self, *, user_id: int, title: str | None, body: str, community_id: int | None = None, kind: str = "confession") -> dict:
        cleaned_title = sanitize_text(title) if title else None
        cleaned_body = sanitize_text(body)

        confession = Content(
            title=cleaned_title,
            body=cleaned_body,
            community_id=community_id,
            user_id=user_id,
            kind=kind,
            status="published",
        )
        self.db.add(confession)
        self.db.commit()
        self.db.refresh(confession)
        return confession.to_dict()
