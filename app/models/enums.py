from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ContentType(str, Enum):
    CONFESSION = "confession"
    ANNOUNCEMENT = "announcement"
    OPPORTUNITY = "opportunity"


class ReactionKind(str, Enum):
    LIKE = "like"
    LOVE = "love"
    FIRE = "fire"
    SAD = "sad"


class ReportCategory(str, Enum):
    SPAM = "spam"
    ABUSE = "abuse"
    HATE = "hate"
    FAKE = "fake"
    OTHER = "other"
