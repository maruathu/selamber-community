# Selamber Community

Selamber Community is a working starter application for a moderated community platform with anonymous confessions, discussion threads, reaction flows, and moderation tooling. It includes a SQLAlchemy data layer, a FastAPI backend, a Telegram bot skeleton, and a lightweight admin dashboard.

## Features
- Anonymous confession posting workflow
- Community creation and listing
- Comments and moderation reporting endpoints
- Built-in stats endpoint for quick dashboard metrics
- Telegram bot command skeleton for community interactions
- SQLite default database with easy local development setup
- Seed data support for demo content

## Quick start

1. Create a virtual environment: `python -m venv .venv`
2. Activate it and install dependencies: `python -m pip install -r requirements.txt`
3. Initialize the database: `python main.py --init-db`
4. Load demo data: `python main.py --seed`
5. Copy `.env.example` to `.env` and set a long random `ADMIN_API_TOKEN`.
6. Start the API: `python main.py --mode api`
7. Or start the Telegram bot: `python main.py --mode bot`

## Available API routes

- `GET /` — API metadata
- `GET /health` — health check
- `GET /communities` — list communities
- `POST /communities` — create a community (admin bearer token required)
- `GET /confessions` — list recent confessions
- `GET /confessions/{id}` — fetch one confession
- `POST /confessions` — create a confession
- `POST /comments` — add a comment
- `POST /reports` — create a report
- `GET /stats` — aggregate counts
- `GET /reports` — list pending reports (admin bearer token required)
- `PATCH /reports/{id}` — resolve or dismiss a report (admin bearer token required)
- `PATCH /confessions/{id}/moderation` — hide or restore a confession (admin bearer token required)
- `GET /moderation/hidden-confessions` — list hidden confessions (admin bearer token required)

The dashboard's admin-token field sends `ADMIN_API_TOKEN` as a bearer credential for community creation and moderation operations. Keep this value private and use HTTPS outside local development.

## Default configuration

The default database is SQLite (`selamber.db`). A `.env` file can override settings using the keys in `.env.example`.

## Project layout
- `app/` contains the domain models, repositories, services, and Telegram bot code.
- `backend/src/` contains the FastAPI app and typed request/response schemas.
- `admin-panel/` contains the browser dashboard.
- `scripts/seed.py` seeds example communities and posts.
- `tests/` contains smoke and API validation tests.

## Docker

```bash
docker compose up --build
```
