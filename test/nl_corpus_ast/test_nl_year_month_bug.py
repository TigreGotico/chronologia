"""Native-reviewer bug ledger for Asturian -- strict xfails.

These are grammatical Asturian phrasings whose *correct* reading is asserted
below, but the locale currently mis-resolves them.  Marked ``strict=True`` so
that the day a fix lands the xpass turns the suite red and these graduate into
plain passing corpus entries.

BUG 1  ``<month> de <year>``: the connecting "de/del" before a bare year is not
       consumed, so the year is dropped and the month falls back to the anchor
       year.  (The juxtaposed form ``avientu 1999`` works -- see
       test_nl_year_month.)
BUG 2  Ordinal weekday-of-month only resolves for 1st..3rd; 4th/5th
       (cuartu/quintu) are dropped even when that occurrence exists.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad
from ._gen import nth_weekday


@pytest.mark.xfail(strict=True, reason="BUG: 'de <year>' after a month is not consumed")
@pytest.mark.parametrize("text,xs,xe", [
    ("avientu de 1999", datetime(1999, 12, 1), datetime(2000, 1, 1)),
    ("xunu de 2020", datetime(2020, 6, 1), datetime(2020, 7, 1)),
    ("xineru de 2000", datetime(2000, 1, 1), datetime(2000, 2, 1)),
])
def test_month_de_year_bug(text, xs, xe):
    s, e = start_end(text)
    assert (s, e) == (ad(xs), ad(xe))


def _high_ordinal_cases():
    out = []
    # 4th weekdays that genuinely exist in March 2017
    for on, n in (("cuartu", 4),):
        for wn, w in (("llunes", 0), ("xueves", 3), ("vienres", 4)):
            d = nth_weekday(2017, 3, w, n)
            assert d is not None
            out.append((f"el {on} {wn} de marzu", datetime(d.year, d.month, d.day)))
    return out


@pytest.mark.xfail(strict=True, reason="BUG: 4th+ ordinal weekday-of-month not resolved")
@pytest.mark.parametrize("text,expected", _high_ordinal_cases())
def test_high_ordinal_weekday_bug(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e - s == timedelta(days=1)
