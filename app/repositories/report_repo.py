from __future__ import annotations

from sqlalchemy import select

from app.models.interaction import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    model = Report

    def pending(self):
        stmt = select(Report).where(Report.status == "pending").order_by(Report.created_at.desc())
        return self.db.scalars(stmt).all()
