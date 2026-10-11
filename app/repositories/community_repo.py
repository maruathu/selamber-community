from __future__ import annotations

from sqlalchemy import select

from app.models.community import Community
from app.repositories.base import BaseRepository


class CommunityRepository(BaseRepository):
    model = Community

    def get_by_slug(self, slug: str):
        stmt = select(Community).where(Community.slug == slug)
        return self.db.scalar(stmt)
