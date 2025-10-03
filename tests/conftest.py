from pathlib import Path

from openpyxl.reader.excel import load_workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import pytest

from pmo.models import Base
from pmo.sample_data import create_sample_data


TESTS_DIR = Path(__file__).parent


@pytest.fixture
def wb():
    _wb = load_workbook(TESTS_DIR / "data.xlsx")
    yield _wb
    _wb.close()


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_dataset(session):
    """Populate the database with an opinionated PMO dataset and return context."""

    data = create_sample_data(session)
    return data
