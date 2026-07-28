# -*- coding: utf-8 -*-
"""Early / mid / late of a *named* month (fr): "début mars", "mi-mars",
"fin mars", plus the "milieu de" / "début de" variants.

The band is the arithmetic third of the parent month, the same equal-thirds
rule as :mod:`test_nl_fuzzy_period` applies to "début du mois".  The parent
month is ``[M-01 00:00, (M+1)-01 00:00)``; its width is split in three equal
timedeltas, so the internal boundaries land on fractional days for the 31- and
28-day months (31/3 d = 10 d 8 h; 28/3 d = 9 d 8 h) and on whole days for the
30-day months.  Every expected edge is pure ``timedelta`` arithmetic done here,
never read back from the parser.

A bare named month with no year binds to the anchor's own year (2017), even
when that month is already past -- there is no prefer-future roll for a scoped
month band.  (The explicit-year form "début mars 2019" is a KNOWN DEFECT: the
year is silently dropped and the band stays in 2017.  That is resolver-owned
behaviour shared with English "early March 2019"; it is NOT asserted here.)

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end, nomatch


def _third(month, part):
    s = datetime(2017, month, 1)
    e = datetime(2018, 1, 1) if month == 12 else datetime(2017, month + 1, 1)
    w = (e - s) / 3
    lo, hi = {"debut": (s, s + w),
              "milieu": (s + w, s + 2 * w),
              "fin": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre",
    12: "décembre",
}


def _cases():
    out = []
    for m, name in _MONTHS.items():
        out.append((f"début {name}", m, "debut"))
        out.append((f"mi-{name}", m, "milieu"))
        out.append((f"fin {name}", m, "fin"))
    return out


@pytest.mark.parametrize("text,month,part", _cases())
def test_named_month_third(text, month, part):
    want_s, want_e = _third(month, part)
    s, e = start_end(text)
    assert (s, e) == (want_s, want_e), f"{text!r} -> {s}..{e}"


# -- the three thirds of one month partition it exactly, no gaps/overlaps ----

@pytest.mark.parametrize("month", list(_MONTHS))
def test_thirds_partition_the_month(month):
    d_s, d_e = start_end(f"début {_MONTHS[month]}")
    m_s, m_e = start_end(f"mi-{_MONTHS[month]}")
    f_s, f_e = start_end(f"fin {_MONTHS[month]}")
    assert d_e == m_s and m_e == f_s          # contiguous
    assert d_s == AstroDate(2017, month, 1)   # opens the month
    end = AstroDate(2018, 1, 1) if month == 12 else AstroDate(2017, month + 1, 1)
    assert f_e == end                          # closes the month


# -- lexical variants all resolve to the same middle third of March ----------

@pytest.mark.parametrize("text", [
    "mi-mars", "mi mars", "milieu mars", "milieu de mars",
])
def test_middle_variants_agree(text):
    assert start_end(text) == _third(3, "milieu")


@pytest.mark.parametrize("text", ["début de mars", "début mars"])
def test_start_variants_agree(text):
    assert start_end(text) == _third(3, "debut")


# -- fractional boundary is exact for the 28-day month -----------------------

def test_february_third_boundaries_are_fractional():
    # 28 / 3 days = 9 d 8 h ; the internal cuts fall at 08:00 and 16:00
    assert start_end("début février") == (
        AstroDate(2017, 2, 1), AstroDate(2017, 2, 10, 8, 0))
    assert start_end("mi-février") == (
        AstroDate(2017, 2, 10, 8, 0), AstroDate(2017, 2, 19, 16, 0))
    assert start_end("fin février") == (
        AstroDate(2017, 2, 19, 16, 0), AstroDate(2017, 3, 1))


@pytest.mark.parametrize("text", ["début", "la fin", "le milieu"])
def test_bare_fuzzy_word_is_not_a_month_third(text):
    nomatch(text)
