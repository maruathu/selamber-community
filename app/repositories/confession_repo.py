from __future__ import annotations

from sqlalchemy import select

from app.models.confession import Confession
from app.repositories.base import BaseRepository


class ConfessionRepository(BaseRepository):
    model = Confession

    def latest(self, *, limit: int = 10):
        stmt = select(Confession).order_by(Confession.created_at.desc()).limit(limit)
        return self.db.scalars(stmt).all()
