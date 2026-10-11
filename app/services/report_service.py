from __future__ import annotations

from app.repositories.report_repo import ReportRepository


class ReportService:
    def __init__(self, db):
        self.db = db
        self.repo = ReportRepository(db)

    def create_report(self, *, content_id: int, user_id: int, category: str, reason: str | None = None) -> dict:
        report = self.repo.create(content_id=content_id, user_id=user_id, category=category, reason=reason, status="pending")
        return report.to_dict()

    def list_pending(self):
        return [report.to_dict() for report in self.repo.pending()]
