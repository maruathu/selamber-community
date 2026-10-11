from __future__ import annotations

from app.repositories.reaction_repo import ReactionRepository


class ReactionService:
    def __init__(self, db):
        self.db = db
        self.reaction_repo = ReactionRepository(db)

    def toggle(self, *, content_id: int, user_id: int, kind: str = "like") -> dict:
        existing = self.reaction_repo.get_for_user(content_id=content_id, user_id=user_id)
        if existing is not None:
            self.reaction_repo.delete(existing)
            return {"status": "removed", "kind": kind, "content_id": content_id, "user_id": user_id}

        reaction = self.reaction_repo.create(content_id=content_id, user_id=user_id, kind=kind)
        return reaction.to_dict()
