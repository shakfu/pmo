from pathlib import Path

from openpyxl.reader.excel import load_workbook

import pytest

TESTS_DIR = Path(__file__).parent

@pytest.fixture
def wb():
    _wb = load_workbook(TESTS_DIR / 'data.xlsx')
    yield _wb
    _wb.close()
