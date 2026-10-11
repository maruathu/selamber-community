from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommunityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=120)
    description: str | None = None


class CommunityCreate(CommunityBase):
    @field_validator("slug")
    @classmethod
    def slugify_slug(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "-")


class CommunityOut(CommunityBase):
    id: int
    is_active: bool = True
    created_at: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ConfessionBase(BaseModel):
    title: str | None = None
    body: str = Field(..., min_length=1, max_length=4000)
    community_id: int | None = None
    kind: str = "confession"


class ConfessionCreate(ConfessionBase):
    telegram_id: int = 0
    first_name: str = "Guest"
    username: str | None = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("body cannot be empty")
        return cleaned


class ConfessionOut(ConfessionBase):
    id: int
    user_id: int | None = None
    status: str = "published"
    created_at: str | None = None
    updated_at: str | None = None
    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    content_id: int
    user_id: int | None = None
    body: str = Field(..., min_length=1, max_length=2000)
    parent_id: int | None = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("body cannot be empty")
        return cleaned


class CommentOut(CommentCreate):
    id: int
    created_at: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ReportCreate(BaseModel):
    content_id: int
    user_id: int
    category: str = "other"
    reason: str | None = None


class ReportOut(ReportCreate):
    id: int
    status: str = "pending"
    created_at: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ReportReview(BaseModel):
    status: Literal["resolved", "dismissed"]


class ContentModeration(BaseModel):
    status: Literal["published", "hidden"]


class StatsOut(BaseModel):
    communities: int
    confessions: int
    comments: int
    reports: int
