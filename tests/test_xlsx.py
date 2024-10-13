# from openpyxl.reader.excel import load_workbook
from openpyxl.workbook.defined_name import DefinedName
import pytest

def test_workbook(wb):
    assert wb
