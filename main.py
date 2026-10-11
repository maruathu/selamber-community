from __future__ import annotations

import argparse

from app.config.settings import settings
from app.database.session import init_db


def run_api() -> None:
    import uvicorn

    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=8000, reload=settings.debug)


def run_bot() -> None:
    from app.bot.dispatcher import start_bot

    start_bot()


def main() -> None:
    parser = argparse.ArgumentParser(description="Selamber Community")
    parser.add_argument("--mode", choices=["api", "bot"], default="api")
    parser.add_argument("--init-db", action="store_true", help="Create database tables")
    parser.add_argument("--seed", action="store_true", help="Populate demo data")
    args = parser.parse_args()

    if args.init_db:
        init_db()
        print("Database initialized.")
        return

    if args.seed:
        from scripts.seed import seed

        seed()
        print("Demo data loaded.")
        return

    if args.mode == "api":
        run_api()
    else:
        run_bot()


if __name__ == "__main__":
    main()
