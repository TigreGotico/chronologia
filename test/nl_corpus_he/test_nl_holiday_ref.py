# -*- coding: utf-8 -*-
"""Holiday references in Hebrew: a well-known holiday named in native script
resolves to its own day-wide span.

The construction under test is ``holiday_ref`` (added to ``he/lang.json``): a
holiday spoken by name ("חנוכה", "פסח", "ראש השנה 2026") resolves to the
holiday's :class:`DateSpan`. Every expected date is derived by hand from
independent published Jewish date tables, cross-checked against this engine's
arithmetic Hebrew calendar. A feast begins the preceding sunset; the date
asserted is the first *full* civil day, the convention those tables tabulate.

Anchor is 2017-06-27 (a Tuesday); "bare" = the next occurrence on or after the
anchor:

    Rosh Hashanah 2017 = 21 Sep      Yom Kippur 2017 = 30 Sep
    Passover      2017 = 11 Apr (past) -> 2018 = 31 Mar;  2026 = 2 Apr
    Hanukkah      2017 = 13 Dec;  2026 = 5 Dec

Cross-script surfaces (Islamic/Chinese named in Hebrew): Eid al-Fitr 2018 =
15 Jun; Chinese New Year 2018 = 16 Feb; Nowruz 2018 = 21 Mar.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch  # noqa: F401


_BARE = [
    ("ראש השנה", (2017, 9, 21)),
    ("יום כיפור", (2017, 9, 30)),
    ("יום הכיפורים", (2017, 9, 30)),
    ("פסח", (2018, 3, 31)),
    ("חג הפסח", (2018, 3, 31)),
    ("חנוכה", (2017, 12, 13)),
    ("עיד אל-פיטר", (2018, 6, 15)),
    ("רמדאן", (2018, 5, 16)),
    ("ראש השנה הסיני", (2018, 2, 16)),
    ("נורוז", (2018, 3, 21)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("פסח 2026", (2026, 4, 2)),
    ("חנוכה 2026", (2026, 12, 5)),
    ("ראש השנה הסיני 2026", (2026, 2, 17)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("next hanukkah", (2017, 12, 13)),
])
def test_cross_script_ignored_english_binds_nothing(text, ymd):
    # A purely English phrase in the Hebrew locale has no bound surface here.
    nomatch(text)


# -- negatives: no holiday word -> nothing binds --------------------------
@pytest.mark.parametrize("text", [
    "מחיר האורז עלה",
    "קערת מרק",
])
def test_no_holiday_no_match(text):
    nomatch(text)
