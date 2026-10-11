from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.config.settings import settings
from backend.src.main import app

client = TestClient(app)


def test_root_and_health_routes() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["status"] == "ok"


def test_community_and_confession_flow(monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_token", "test-admin-token")
    headers = {"Authorization": "Bearer test-admin-token"}
    slug = f"launch-club-{uuid4().hex[:8]}"
    assert client.post(
        "/communities",
        json={"name": "Unauthorized", "slug": f"unauthorized-{uuid4().hex[:8]}"},
    ).status_code == 401
    community = client.post(
        "/communities",
        json={"name": "Launch Club", "slug": slug, "description": "Product launch conversations"},
        headers=headers,
    )
    assert community.status_code == 201, community.text
    community_data = community.json()
    assert community_data["slug"] == slug

    confession = client.post(
        "/confessions",
        json={
            "title": "Hello world",
            "body": "This is a sample confession from the API.",
            "community_id": community_data["id"],
            "telegram_id": 9999,
            "first_name": "Tester",
            "username": "tester",
        },
    )
    assert confession.status_code == 201, confession.text
    body = confession.json()
    assert body["title"] == "Hello world"
    assert body["body"] == "This is a sample confession from the API."

    stats = client.get("/stats")
    assert stats.status_code == 200
    payload = stats.json()
    assert payload["communities"] >= 1
    assert payload["confessions"] >= 1


def test_moderation_requires_token_and_hides_content(monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_token", "")
    assert client.get("/reports").status_code == 503
    monkeypatch.setattr(settings, "admin_api_token", "test-admin-token")
    confession = client.post(
        "/confessions",
        json={
            "body": "A post used to verify moderation actions.",
            "telegram_id": 87654321,
            "first_name": "Moderator test",
        },
    )
    assert confession.status_code == 201, confession.text
    confession_data = confession.json()

    report = client.post(
        "/reports",
        json={
            "content_id": confession_data["id"],
            "user_id": confession_data["user_id"],
            "category": "spam",
            "reason": "Test report",
        },
    )
    assert report.status_code == 201, report.text
    report_id = report.json()["id"]
    confession_id = confession_data["id"]

    assert client.get("/reports").status_code == 401
    assert client.patch(
        f"/reports/{report_id}",
        json={"status": "resolved"},
    ).status_code == 401

    headers = {"Authorization": "Bearer test-admin-token"}
    pending = client.get("/reports", headers=headers)
    assert pending.status_code == 200
    assert any(item["id"] == report_id for item in pending.json())

    reviewed = client.patch(
        f"/reports/{report_id}",
        json={"status": "resolved"},
        headers=headers,
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "resolved"
    assert client.patch(
        f"/reports/{report_id}",
        json={"status": "dismissed"},
        headers=headers,
    ).status_code == 409

    hidden = client.patch(
        f"/confessions/{confession_id}/moderation",
        json={"status": "hidden"},
        headers=headers,
    )
    assert hidden.status_code == 200
    assert hidden.json()["status"] == "hidden"
    assert client.get("/moderation/hidden-confessions").status_code == 401
    hidden_posts = client.get("/moderation/hidden-confessions", headers=headers)
    assert hidden_posts.status_code == 200
    assert any(item["id"] == confession_id for item in hidden_posts.json())
    assert client.get(f"/confessions/{confession_id}").status_code == 404
    assert all(item["id"] != confession_id for item in client.get("/confessions").json())

    restored = client.patch(
        f"/confessions/{confession_id}/moderation",
        json={"status": "published"},
        headers=headers,
    )
    assert restored.status_code == 200
    assert restored.json()["status"] == "published"
