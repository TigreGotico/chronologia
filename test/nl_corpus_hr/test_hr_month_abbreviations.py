"""Croatian abbreviated month names (CLDR 47 ``months.format.abbreviated``).

Croatian could not read an abbreviated month at all before this file's
companion fix to ``locale/hr/month_*.voc`` -- ``extract_timespan("15. sij
2020", "hr", anchor=...)`` returned ``None``.  CLDR ships the abbreviated
surface bare (no trailing dot in the data itself), but a day-month-year date
still carries the ordinal dot after the day number ("15."); a further dot
after the month abbreviation ("15. sij. 2020") is also idiomatic and must
resolve the same way, since the tokenizer strips a trailing dot before
vocabulary matching. Expected dates are computed by hand, independent of the
parser.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, parse


@pytest.mark.parametrize("text,y,mo,d", [
    ("15. sij 2020", 2020, 1, 15),
    ("15. velj 2020", 2020, 2, 15),
    ("15. ožu 2020", 2020, 3, 15),
    ("15. tra 2020", 2020, 4, 15),
    ("15. svi 2020", 2020, 5, 15),
    ("15. lip 2020", 2020, 6, 15),
    ("15. srp 2020", 2020, 7, 15),
    ("15. kol 2020", 2020, 8, 15),
    ("15. ruj 2020", 2020, 9, 15),
    ("15. lis 2020", 2020, 10, 15),
    ("15. stu 2020", 2020, 11, 15),
    ("15. pro 2020", 2020, 12, 15),
])
def test_full_dmy_abbreviated_month(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text", ["15. sij. 2020", "25. lip. 1991"])
def test_dotted_abbreviation_also_resolves(text):
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text", [
    "15. sij 2020", "15. sij. 2020", "15. pro 2020",
])
def test_abbreviated_month_leaves_no_remainder(text):
    assert parse(text).remainder == ""


def test_full_month_name_unaffected_by_abbreviation():
    # "prosinac" (December, full) must not be shadowed by the new "pro".
    assert start("15. prosinca 2020") == ad(datetime(2020, 12, 15))
    assert start("15. ožujka 2020") == ad(datetime(2020, 3, 15))
