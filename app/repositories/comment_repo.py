from __future__ import annotations

from sqlalchemy import select

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository):
    model = Comment

    def list_for_content(self, content_id: int):
        stmt = select(Comment).where(Comment.content_id == content_id).order_by(Comment.created_at.asc())
        return self.db.scalars(stmt).all()
