from __future__ import annotations

from sqlalchemy import select

from app.models.content import Content
from app.repositories.base import BaseRepository


class ContentRepository(BaseRepository):
    model = Content

    def list_recent(self, *, limit: int = 20):
        stmt = (
            select(Content)
            .where(Content.status == "published")
            .order_by(Content.created_at.desc())
            .limit(limit)
        )
        return self.db.scalars(stmt).all()
