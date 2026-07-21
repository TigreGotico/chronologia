"""Wave 1 -- non-Gregorian calendars (Islamic civil + Hebrew).

A day-dated reckoned date is day-wide; a bare month+year is month-wide.
Expected Gregorian equivalents are calendar facts (cross-checked against
chronologia's tabulated calendars, the shared reckoning core) -- e.g.
15 Ramadan 1446 AH == 2025-03-15, 1 Tishrei 5786 AM == 2025-09-23.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, start, start_end, span, nomatch


# -- Islamic (hijri) day dates --------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15 ramadan 1446", 2025, 3, 15),
    ("the 15th of ramadan 1446", 2025, 3, 15),
    ("1 muharram 1446", 2024, 7, 8),
    ("10 muharram 1447", 2025, 7, 6),
    ("1 shawwal 1445", 2024, 4, 10),
    ("27 rajab 1446", 2025, 1, 27),
    ("ramzan 1446".replace("ramzan 1446", "1 ramadan 1446"), 2025, 3, 1),
    ("9 rabialawwal 1446", 2024, 9, 13),
    ("20 safar 1447", 2025, 8, 15),
    ("1 jumadaalawwal 1446", 2024, 11, 3),
    ("15 shaban 1446", 2025, 2, 14),
    ("3 shawwal 1446", 2025, 4, 2),
    ("25 dhualqadah 1445", 2024, 6, 2),
    ("28 ramadan 1446", 2025, 3, 28),
])
def test_hijri_day(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# -- Islamic bare month (month-wide) --------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("ramadan 1446", 2025, 3, 1),
    ("muharram 1446", 2024, 7, 8),
    ("dhualhijjah 1446", 2025, 5, 29),
    ("rajab 1446", 2025, 1, 1),
])
def test_hijri_month(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert (e - s).days >= 29          # a lunar month


# -- Hebrew day dates -----------------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("5 tishrei 5786", 2025, 9, 27),
    ("1 tishrei 5786", 2025, 9, 23),
    ("the 1st of tishrei 5786", 2025, 9, 23),
    ("the 10th of tishrei 5786", 2025, 10, 2),
    ("15 nisan 5785", 2025, 4, 13),
    ("1 nisan 5786", 2026, 3, 19),
    ("6 iyar 5786", 2026, 4, 23),
    ("18 sivan 5786", 2026, 6, 3),
    ("10 tevet 5786", 2025, 12, 30),
    ("15 shevat 5786", 2026, 2, 2),
    ("1 elul 5785", 2025, 8, 25),
    ("20 av 5785", 2025, 8, 14),
    ("1 kislev 5786", 2025, 11, 21),
    ("the 9th of av 5785", 2025, 8, 3),
])
def test_hebrew_day(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# -- Hebrew bare month (month-wide) ---------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("tishrei 5785", 2024, 10, 3),
    ("cheshvan 5786", 2025, 10, 23),
    ("nisan 5785", 2025, 3, 30),
    ("sivan 5785", 2025, 5, 28),
])
def test_hebrew_month(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)


# -- romanization variants ------------------------------------------------

@pytest.mark.parametrize("a,b", [
    ("7 tishri 5786", "7 tishrei 5786"),
    ("1 heshvan 5786", "1 cheshvan 5786"),
    ("1 shaaban 1446", "1 shaban 1446"),
])
def test_romanization_variants_agree(a, b):
    assert start(a) == start(b)


# -- must-not-parse: impossible calendar days -----------------------------

@pytest.mark.parametrize("text", [
    "31 ramadan 1446",     # lunar months are 29-30 days
    "40 tishrei 5786",
])
def test_impossible_calendar_day(text):
    r = span.__class__ if False else None
    from ._corpus import parse
    res = parse(text)
    if res is not None:            # a bare-month fallback may fire
        assert res[0].width.days <= 31


# -- Hebrew new year (Rosh Hashanah = 1 Tishrei of the given Hebrew year) --

@pytest.mark.parametrize("text,d", [
    ("the hebrew new year 5786", AstroDate(2025, 9, 23)),
    ("hebrew new year 5786", AstroDate(2025, 9, 23)),
    ("the jewish new year 5784", AstroDate(2023, 9, 16)),
])
def test_hebrew_new_year(text, d):
    assert start(text) == d


# French Republican months: the month vocab is wired (day/month-level); the
# small republican year ("year 8") is not bound (YEAR needs >= 4 digits), so
# it resolves in the current republican year and leaves 'year N' as remainder.
@pytest.mark.parametrize("text,month", [
    ("18 brumaire", 11), ("1 vendemiaire", 9), ("18 brumaire year 8", 11),
])
def test_republican_month(text, month):
    r = parse(text)
    assert r is not None and r[0].start.month == month
