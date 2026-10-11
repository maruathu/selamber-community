from __future__ import annotations

from contextlib import asynccontextmanager
from hmac import compare_digest

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings
from app.database.session import SessionLocal, init_db
from app.models.comment import Comment
from app.models.community import Community
from app.models.content import Content
from app.models.interaction import Report
from app.repositories.community_repo import CommunityRepository
from app.repositories.content_repo import ContentRepository
from app.repositories.user_repo import UserRepository
from app.services.comment_service import CommentService
from app.services.confession_service import ConfessionService
from app.services.report_service import ReportService
from backend.src.schemas import (
    CommentCreate,
    CommentOut,
    ContentModeration,
    CommunityCreate,
    CommunityOut,
    ConfessionCreate,
    ConfessionOut,
    ReportCreate,
    ReportOut,
    ReportReview,
    StatsOut,
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Selamber Community API",
    version="1.0.0",
    description="Community moderation and confession platform API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bearer_scheme = HTTPBearer(auto_error=False)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    configured_token = settings.admin_api_token
    if not configured_token:
        raise HTTPException(status_code=503, detail="Admin API is not configured")
    if credentials is None or not compare_digest(credentials.credentials, configured_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
def root() -> dict:
    return {"name": "Selamber Community API", "version": "1.0.0", "status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/communities", response_model=list[CommunityOut])
def list_communities() -> list[dict]:
    with SessionLocal() as db:
        communities = CommunityRepository(db).list()
        return [community.to_dict() for community in communities]


@app.post(
    "/communities",
    response_model=CommunityOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_community(payload: CommunityCreate) -> dict:
    with SessionLocal() as db:
        repo = CommunityRepository(db)
        existing = repo.get_by_slug(payload.slug)
        if existing is not None:
            raise HTTPException(status_code=400, detail="Community slug already exists")
        community = repo.create(name=payload.name, slug=payload.slug, description=payload.description, is_active=True)
        return community.to_dict()


@app.get("/confessions", response_model=list[ConfessionOut])
def list_confessions() -> list[dict]:
    with SessionLocal() as db:
        content = ContentRepository(db).list_recent(limit=20)
        return [item.to_dict() for item in content]


@app.get(
    "/moderation/hidden-confessions",
    response_model=list[ConfessionOut],
    dependencies=[Depends(require_admin)],
)
def list_hidden_confessions() -> list[dict]:
    with SessionLocal() as db:
        hidden = db.query(Content).filter(Content.status == "hidden").order_by(Content.created_at.desc()).all()
        return [item.to_dict() for item in hidden]


@app.get("/confessions/{confession_id}", response_model=ConfessionOut)
def get_confession(confession_id: int) -> dict:
    with SessionLocal() as db:
        confession = db.get(Content, confession_id)
        if confession is None or confession.status != "published":
            raise HTTPException(status_code=404, detail="Confession not found")
        return confession.to_dict()


@app.post("/confessions", response_model=ConfessionOut, status_code=status.HTTP_201_CREATED)
def create_confession(payload: ConfessionCreate) -> dict:
    with SessionLocal() as db:
        if not payload.body.strip():
            raise HTTPException(status_code=400, detail="Body cannot be empty")

        user_repo = UserRepository(db)
        user = user_repo.get_or_create(
            telegram_id=payload.telegram_id,
            first_name=payload.first_name,
            username=payload.username,
        )
        service = ConfessionService(db)
        item = service.create(
            user_id=user.id,
            title=payload.title,
            body=payload.body,
            community_id=payload.community_id,
            kind=payload.kind,
        )
        return item


@app.post("/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate) -> dict:
    with SessionLocal() as db:
        if db.get(Content, payload.content_id) is None:
            raise HTTPException(status_code=404, detail="Content not found")
        service = CommentService(db)
        return service.add_comment(
            content_id=payload.content_id,
            user_id=payload.user_id or 0,
            body=payload.body,
            parent_id=payload.parent_id,
        )


@app.get("/reports", response_model=list[ReportOut], dependencies=[Depends(require_admin)])
def list_reports() -> list[dict]:
    with SessionLocal() as db:
        service = ReportService(db)
        return service.list_pending()


@app.patch("/reports/{report_id}", response_model=ReportOut, dependencies=[Depends(require_admin)])
def review_report(report_id: int, payload: ReportReview) -> dict:
    with SessionLocal() as db:
        report = db.get(Report, report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")
        if report.status != "pending":
            raise HTTPException(status_code=409, detail="Report has already been reviewed")
        report.status = payload.status
        db.commit()
        db.refresh(report)
        return report.to_dict()


@app.patch(
    "/confessions/{confession_id}/moderation",
    response_model=ConfessionOut,
    dependencies=[Depends(require_admin)],
)
def moderate_confession(confession_id: int, payload: ContentModeration) -> dict:
    with SessionLocal() as db:
        confession = db.get(Content, confession_id)
        if confession is None:
            raise HTTPException(status_code=404, detail="Confession not found")
        confession.status = payload.status
        db.commit()
        db.refresh(confession)
        return confession.to_dict()


@app.post("/reports", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate) -> dict:
    with SessionLocal() as db:
        if db.get(Content, payload.content_id) is None:
            raise HTTPException(status_code=404, detail="Content not found")
        service = ReportService(db)
        report = service.create_report(
            content_id=payload.content_id,
            user_id=payload.user_id,
            category=payload.category,
            reason=payload.reason,
        )
        return report


@app.get("/stats", response_model=StatsOut)
def stats() -> dict:
    with SessionLocal() as db:
        communities = db.query(Community).count()
        confessions = db.query(Content).filter(Content.kind == "confession").count()
        comments = db.query(Comment).count()
        reports = db.query(Report).count()
        return {"communities": communities, "confessions": confessions, "comments": comments, "reports": reports}
