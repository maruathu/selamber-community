from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository:
    model: type[Base]

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int) -> Any | None:
        return self.db.get(self.model, item_id)

    def list(self, *, limit: int | None = None) -> list[Any]:
        stmt = select(self.model)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, **kwargs: Any) -> Any:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, item: Any, **kwargs: Any) -> Any:
        for key, value in kwargs.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Any) -> None:
        self.db.delete(item)
        self.db.commit()
