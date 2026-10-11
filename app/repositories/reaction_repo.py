from __future__ import annotations

from sqlalchemy import select

from app.models.interaction import Reaction
from app.repositories.base import BaseRepository


class ReactionRepository(BaseRepository):
    model = Reaction

    def get_for_user(self, *, content_id: int, user_id: int):
        stmt = select(Reaction).where(Reaction.content_id == content_id, Reaction.user_id == user_id)
        return self.db.scalar(stmt)
