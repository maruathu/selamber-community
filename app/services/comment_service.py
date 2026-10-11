from __future__ import annotations

from app.repositories.comment_repo import CommentRepository
from app.utils.text import sanitize_text


class CommentService:
    def __init__(self, db):
        self.db = db
        self.comment_repo = CommentRepository(db)

    def add_comment(self, *, content_id: int, user_id: int, body: str, parent_id: int | None = None) -> dict:
        cleaned_body = sanitize_text(body)
        comment = self.comment_repo.create(content_id=content_id, user_id=user_id, body=cleaned_body, parent_id=parent_id)
        return comment.to_dict()
