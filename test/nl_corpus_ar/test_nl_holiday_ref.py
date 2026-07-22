# -*- coding: utf-8 -*-
"""Holiday references in Arabic: a well-known holiday named in native script
resolves to its own day-wide span.

The construction under test is ``holiday_ref`` (added to ``ar/lang.json``): a
holiday spoken by name ("عيد الفطر", "متى عيد الفطر", "عيد الفطر 2026") resolves
to the holiday's :class:`DateSpan`. Every expected date is derived by hand from
independent published tables, cross-checked against this engine's own tabulated
calendars.

Anchor is 2017-06-27 (a Tuesday); "bare" = the next occurrence on or after the
anchor, so a feast already past in 2017 rolls to 2018. Islamic dates come from
the Umm al-Qura table (basis ``tabulated``):

    Eid al-Fitr    2017 = 25 Jun (past) -> 2018 = 15 Jun;  2026 = 20 Mar
    Ramadan start  2017 = 27 May (past) -> 2018 = 16 May
    Eid al-Adha    2017 = 1 Sep
    Islamic New Yr 2017 = 21 Sep      Ashura 2017 = 30 Sep      Mawlid 2017 = 30 Nov

Hebrew (arithmetic) and Chinese (tabulated) feasts named with their Arabic
surfaces:  Passover 2018 = 31 Mar; Hanukkah 2017 = 13 Dec; Chinese New Year
2018 = 16 Feb; Nowruz 2018 = 21 Mar.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch  # noqa: F401


_BARE = [
    ("عيد الفطر", (2018, 6, 15)),
    ("العيد الصغير", (2018, 6, 15)),
    ("عيد الأضحى", (2017, 9, 1)),
    ("رأس السنة الهجرية", (2017, 9, 21)),
    ("عاشوراء", (2017, 9, 30)),
    ("المولد النبوي", (2017, 11, 30)),
    ("رأس السنة اليهودية", (2017, 9, 21)),
    ("يوم الغفران", (2017, 9, 30)),
    ("عيد الفصح اليهودي", (2018, 3, 31)),
    ("حانوكا", (2017, 12, 13)),
    ("رأس السنة الصينية", (2018, 2, 16)),
    ("نوروز", (2018, 3, 21)),
    ("ديوالي", (2017, 10, 19)),
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("عيد الفطر 2026", (2026, 3, 20)),
    ("رأس السنة الصينية 2026", (2026, 2, 17)),
    ("ديوالي 2026", (2026, 11, 8)),
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("متى عيد الفطر", (2018, 6, 15)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


# -- negatives: no holiday word -> nothing binds --------------------------
@pytest.mark.parametrize("text", [
    "سعر الأرز ارتفع",
    "طبق من الطعام",
    "اجتماع عمل",
])
def test_no_holiday_no_match(text):
    nomatch(text)
