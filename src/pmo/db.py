"""Shared SQLAlchemy session/engine utilities for the PMO project."""

from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


DEFAULT_DATABASE_URL = "sqlite:///pmo.db"


@lru_cache(maxsize=1)
def get_engine(database_url: str | None = None):
    """Return a memoized SQLAlchemy engine for the provided URL."""

    url = database_url or os.getenv("PMO_DATABASE_URL", DEFAULT_DATABASE_URL)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, connect_args=connect_args)


def create_session_factory(database_url: str | None = None):
    """Create a session factory bound to the project metadata."""

    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
