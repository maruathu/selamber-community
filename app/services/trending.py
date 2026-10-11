from __future__ import annotations

from sqlalchemy import func, select

from app.models.comment import Comment
from app.models.content import Content
from app.models.interaction import Reaction


class TrendingService:
    def __init__(self, db):
        self.db = db

    def top_content(self, *, limit: int = 5):
        score = (
            select(
                Content.id,
                Content.title,
                func.count(Reaction.id).label("reaction_count"),
                func.count(Comment.id).label("comment_count"),
            )
            .select_from(Content)
            .outerjoin(Reaction, Reaction.content_id == Content.id)
            .outerjoin(Comment, Comment.content_id == Content.id)
            .group_by(Content.id, Content.title)
            .order_by((func.count(Reaction.id) + func.count(Comment.id)).desc())
            .limit(limit)
        )
        return self.db.execute(score).all()
