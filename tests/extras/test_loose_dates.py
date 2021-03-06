import pytest
from tests.common import Rules

from json_syntax.extras import loose_dates as exam
from json_syntax.helpers import JSON2PY, PY2JSON, INSP_PY, INSP_JSON, python_minor

from datetime import date, datetime


@pytest.mark.skipif(
    python_minor < (3, 7), reason="datetime.isoformat not supported before python 3.7"
)
def test_iso_dates_loose():
    "Test the iso_dates_loose handles dates using ISO8601 and accepts datetimes."

    decoder = exam.iso_dates_loose(verb=JSON2PY, typ=date, ctx=Rules())
    assert decoder("1776-07-04") == date(1776, 7, 4)
    assert decoder("6543-02-01T09:09:09") == date(6543, 2, 1)

    encoder = exam.iso_dates_loose(verb=PY2JSON, typ=date, ctx=Rules())
    assert encoder(date(1776, 7, 4)) == "1776-07-04"

    inspect = exam.iso_dates_loose(verb=INSP_PY, typ=date, ctx=Rules())
    assert inspect(date(1776, 7, 4))
    assert not inspect(datetime(1776, 7, 4, 3, 3))
    assert not inspect("2000-01-01")
    assert not inspect("2000-01-01T03:03:03")
    assert not inspect("string")

    inspect = exam.iso_dates_loose(verb=INSP_JSON, typ=date, ctx=Rules())
    assert not inspect(date(1776, 7, 4))
    assert not inspect(datetime(1776, 7, 4, 3, 3))
    assert inspect("2000-01-01")
    assert inspect("2000-01-01T03:03:03")
    assert not inspect("string")
