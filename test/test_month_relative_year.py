"""A relative year phrase after a month names the year.

"noviembre del año que viene" is November of next year, and "enero del año
pasado" is January of last year, whichever month the anchor is in.  The
marker may come before the year noun ("del próximo año", "next year") or
after it ("del año que viene", "de l'année prochaine").  A marker right
after the month ("marzo pasado") still names the last March.

The anchor is Saturday 2026-10-17 12:00.  The golds are calendar arithmetic.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("lang, text, year, month", [
    ("es", "noviembre del año que viene", 2027, 11),
    ("es", "noviembre del año pasado", 2025, 11),
    ("es", "enero del año pasado", 2025, 1),
    ("es", "enero del año que viene", 2027, 1),
    ("es", "noviembre del año siguiente", 2027, 11),
    ("es", "en noviembre del año que viene", 2027, 11),
    ("pt", "novembro do ano que vem", 2027, 11),
    ("pt", "janeiro do ano passado", 2025, 1),
    ("fr", "novembre de l'année prochaine", 2027, 11),
    ("fr", "janvier de l'année dernière", 2025, 1),
    ("ca", "novembre de l'any que ve", 2027, 11),
    ("gl", "novembro do ano que vén", 2027, 11),
    # the marker right after the month names the month, not the year
    ("es", "marzo pasado", 2026, 3),
    ("es", "marzo que viene", 2027, 3),
    ("fr", "mars dernier", 2026, 3),
    ("en", "march of this year", 2026, 3),
])
def test_month_of_a_relative_year(lang, text, year, month):
    r = extract_timespan(text, lang, ANCHOR)
    end = (year + 1, 1) if month == 12 else (year, month + 1)
    assert (r.span.start, r.span.end, r.remainder) == (
        AstroDate(year, month, 1), AstroDate(*end, 1), "")


@pytest.mark.parametrize("lang, text, day", [
    # 30 November 2027 is a Tuesday
    ("en", "the last friday of november next year", (2027, 11, 26)),
    ("en", "the last friday of november of next year", (2027, 11, 26)),
    ("es", "el último viernes de noviembre del próximo año", (2027, 11, 26)),
    ("es", "el último viernes de noviembre del año que viene", (2027, 11, 26)),
    # 31 October 2025 is a Friday
    ("es", "el último viernes de octubre del año pasado", (2025, 10, 31)),
    # 31 October 2027 is a Sunday
    ("es", "el último viernes del mes de octubre del año que viene",
     (2027, 10, 29)),
    # 1 January 2027 is a Friday
    ("es", "el primer lunes de enero del año que viene", (2027, 1, 4)),
])
def test_weekday_of_a_month_of_a_relative_year(lang, text, day):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*day), "")
