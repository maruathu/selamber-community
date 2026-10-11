from __future__ import annotations

from app.repositories.report_repo import ReportRepository


class ModerationService:
    def __init__(self, db):
        self.db = db
        self.report_repo = ReportRepository(db)

    def moderate_content(self, content_id: int) -> dict:
        pending_reports = self.report_repo.pending()
        flagged = [report for report in pending_reports if report.content_id == content_id]
        if not flagged:
            return {"status": "clear", "content_id": content_id}
        return {"status": "flagged", "content_id": content_id, "reports": len(flagged)}
