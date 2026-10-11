from __future__ import annotations

from app.database.session import SessionLocal, init_db
from app.models.comment import Comment
from app.models.community import Community
from app.models.content import Content
from app.models.interaction import Report
from app.models.user import User


def seed() -> None:
    init_db()
    with SessionLocal() as db:
        if not db.query(Community).first():
            communities = [
                Community(name="General", slug="general", description="General community forum"),
                Community(name="Announcements", slug="announcements", description="Official updates and event information"),
                Community(name="Support", slug="support", description="Peer support and advice"),
            ]
            db.add_all(communities)
            db.commit()

        if not db.query(User).first():
            users = [
                User(telegram_id=1001, first_name="Alicia", username="alice"),
                User(telegram_id=1002, first_name="Boris", username="boris"),
            ]
            db.add_all(users)
            db.commit()

        if not db.query(Content).first():
            general = db.query(Community).filter_by(slug="general").one()
            support = db.query(Community).filter_by(slug="support").one()
            alice = db.query(User).filter_by(telegram_id=1001).one()
            boris = db.query(User).filter_by(telegram_id=1002).one()

            posts = [
                Content(title="Welcome", body="This is the first Selamber community post.", user_id=alice.id, community_id=general.id, kind="confession"),
                Content(title="Study group", body="Anyone up for a weekend study circle?", user_id=boris.id, community_id=support.id, kind="confession"),
            ]
            db.add_all(posts)
            db.commit()
            db.refresh(posts[0])
            db.add(Comment(content_id=posts[0].id, user_id=boris.id, body="Count me in!"))
            db.add(Report(content_id=posts[0].id, user_id=alice.id, category="other", reason="Checking moderation flow", status="pending"))
            db.commit()


if __name__ == "__main__":
    seed()
    print("Database seeded.")
