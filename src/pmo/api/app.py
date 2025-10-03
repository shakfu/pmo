"""FastAPI application exposing REST endpoints and an admin UI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..db import create_session_factory, get_engine
from .admin import setup_admin
from .routers import router


def create_app(database_url: str | None = None) -> FastAPI:
    engine = get_engine(database_url)
    session_factory = create_session_factory(database_url)

    app = FastAPI(title="PMO Admin API", version="0.1.0")
    app.state.session_factory = session_factory
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.state.admin = setup_admin(app, engine)

    @app.get("/health", tags=["meta"])
    def healthcheck():
        return {"status": "ok"}

    return app


app = create_app()
