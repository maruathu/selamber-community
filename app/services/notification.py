from __future__ import annotations


class NotificationService:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def send(self, *, recipient: str, message: str) -> dict:
        return {"recipient": recipient, "message": message, "sent": True}
