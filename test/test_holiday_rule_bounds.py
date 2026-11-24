"""A holiday rule with a length or until bound (TigreGotico/chronologia#1373)."""
from datetime import date, datetime

import pytest

from chronologia import extract_event, extract_recurrence

ANCHOR = datetime(2026, 11, 24, 9)
ISSUE = pytest.mark.xfail(
    strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1373")

# Easter Sunday in the three years from the anchor.
EASTERS = [date(2027, 3, 28), date(2028, 4, 16), date(2029, 4, 1)]


def days(spans):
    return [date(s.start.year, s.start.month, s.start.day) for s in spans]


@ISSUE
@pytest.mark.parametrize("extract", [extract_recurrence, extract_event])
def test_easter_for_three_years(extract):
    got = extract("every easter for 3 years", "en", ANCHOR)
    assert days(got.recurrence.occurrences(ANCHOR, count=10)) == EASTERS


@ISSUE
def test_easter_for_three_years_leaves_no_remainder():
    assert extract_recurrence("every easter for 3 years", "en", ANCHOR).remainder == ""


@ISSUE
def test_portuguese_holidays_until_a_year():
    plain = extract_recurrence("every public holiday in portugal", "en", ANCHOR)
    want = days(plain.recurrence.occurrences(ANCHOR, until=datetime(2030, 1, 1)))
    got = extract_recurrence("every public holiday in portugal until 2030", "en", ANCHOR)
    assert got.remainder == ""
    assert days(got.recurrence.occurrences(ANCHOR, count=200)) == want
