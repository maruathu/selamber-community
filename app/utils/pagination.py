from __future__ import annotations


def paginate(items, page: int = 1, per_page: int = 10):
    start = (page - 1) * per_page
    end = start + per_page
    total = len(items)
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "items": items[start:end],
    }
