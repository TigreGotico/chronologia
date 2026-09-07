"""Slovak abbreviated month names (CLDR 47 ``months.format.abbreviated``).

Slovak could not read an abbreviated month at all before this file's
companion fix to ``locale/sk/month_*.voc`` -- ``extract_timespan("15. jan
2020", "sk", anchor=...)`` returned ``None`` for nine of the twelve months
(``máj``/``jún``/``júl`` already shipped as full nominative forms and needed
no change). CLDR ships the abbreviated surface bare; a day-month-year date
still carries the ordinal dot after the day number ("15."), and a further
dot after the month abbreviation ("15. jan. 2020") is also idiomatic and
must resolve the same way, since the tokenizer strips a trailing dot before
vocabulary matching. Expected dates are computed by hand, independent of the
parser.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, parse


@pytest.mark.parametrize("text,y,mo,d", [
    ("15. jan 2020", 2020, 1, 15),
    ("15. feb 2020", 2020, 2, 15),
    ("15. mar 2020", 2020, 3, 15),
    ("15. apr 2020", 2020, 4, 15),
    ("15. máj 2020", 2020, 5, 15),
    ("15. jún 2020", 2020, 6, 15),
    ("15. júl 2020", 2020, 7, 15),
    ("15. aug 2020", 2020, 8, 15),
    ("15. sep 2020", 2020, 9, 15),
    ("15. okt 2020", 2020, 10, 15),
    ("15. nov 2020", 2020, 11, 15),
    ("15. dec 2020", 2020, 12, 15),
])
def test_full_dmy_abbreviated_month(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text", ["15. jan. 2020", "25. dec. 1991"])
def test_dotted_abbreviation_also_resolves(text):
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text", [
    "15. jan 2020", "15. jan. 2020", "15. dec 2020",
])
def test_abbreviated_month_leaves_no_remainder(text):
    assert parse(text).remainder == ""


def test_full_month_name_unaffected_by_abbreviation():
    # "december" (December, full) must not be shadowed by the new "dec".
    assert start("15. decembra 2020") == ad(datetime(2020, 12, 15))
    assert start("15. marca 2020") == ad(datetime(2020, 3, 15))
