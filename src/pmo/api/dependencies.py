"""FastAPI dependency utilities for database access."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from ..db import create_session_factory


def _resolve_session_factory(request: Request):
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        session_factory = create_session_factory()
        request.app.state.session_factory = session_factory
    return session_factory


def get_session(request: Request) -> Generator[Session, None, None]:
    session_factory = _resolve_session_factory(request)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def session_dependency(session: Session = Depends(get_session)) -> Session:
    return session
