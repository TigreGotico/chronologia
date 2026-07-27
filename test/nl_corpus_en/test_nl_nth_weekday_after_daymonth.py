"""The Nth <weekday> strictly after a day-of-month anchor.

"the first Friday after the 15th" = the 1st Friday whose date is strictly
greater than the 15th of the anchor's current month; "the second ..." = the
2nd such Friday; a bare "the Friday after the 15th" (no ordinal) means the
first.  The day-of-month names the anchor's OWN calendar month -- it is a
within-month reference, not a prefer-future roll -- so the result may fall
before the anchor.

Anchor is 2017-06-27 (a Tuesday, 13:04).  June 2017 Fridays are
2, 9, 16, 23, 30; the 15th is a Thursday, so the 1st Friday after it is
Jun 16 and the 2nd is Jun 23 (all hand-derived).
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, span, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    # June 2017: 15th = Thu; Fridays after are 16, 23, 30
    ("the first Friday after the 15th", date(2017, 6, 16)),
    ("the second Friday after the 15th", date(2017, 6, 23)),
    ("the third Friday after the 15th", date(2017, 6, 30)),
    # no ordinal == first
    ("the Friday after the 15th", date(2017, 6, 16)),
    # June 2017: 1st = Thu; Mondays after are 5, 12, 19
    ("the first Monday after the 1st", date(2017, 6, 5)),
    ("the second Monday after the 1st", date(2017, 6, 12)),
    # June 2017: 10th = Sat; Tuesdays after are 13, 20, 27
    ("the third Tuesday after the 10th", date(2017, 6, 27)),
    ("the first Tuesday after the 10th", date(2017, 6, 13)),
])
def test_nth_weekday_after_daymonth(text, expected):
    s = span(text)
    assert s.start == _ad(expected), text


@pytest.mark.parametrize("text,expected", [
    ("the first Friday after the 15th", date(2017, 6, 16)),
    ("the second Friday after the 15th", date(2017, 6, 23)),
])
def test_daymonth_and_ordinal_not_stranded(text, expected):
    """The ordinal and the day-of-month are both consumed (no remainder)."""
    r = parse(text)
    assert r is not None
    assert r[0].start == _ad(expected)
    assert r[1] == "", f"stranded remainder: {r[1]!r}"


def test_span_is_one_day():
    s = span("the first Friday after the 15th")
    assert (s.end - s.start).days == 1


# -- regression pins: the collision family must stay byte-identical --------

def test_scoped_ordinal_third_friday_of_march_unchanged():
    # "the third Friday of March" -> nth-weekday-of-month (#288), NOT touched
    assert start("the third Friday of March") == AstroDate(2017, 3, 17)


def test_weekday_after_next_unchanged():
    # "the Friday after next" -> weekend/next machinery, NOT a day-of-month
    r = parse("the Friday after next")
    assert r is not None
