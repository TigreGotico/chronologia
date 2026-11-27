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

A bare named month with no year takes the year the month alone takes (ruling 1,
changed on 26 November 2026; before, it bound to the anchor's own year 2017
even when the month was already past): 2017 for a month that holds or follows
the anchor, 2018 for one that has ended before it (janvier to mai).  (The explicit-year form "début mars 2019" is a KNOWN DEFECT: the
year is silently dropped and the band stays in 2017.  That is resolver-owned
behaviour shared with English "early March 2019"; it is NOT asserted here.)

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, start_end, nomatch


def _year(month):
    # ruling 1: a month that has ended at the anchor (June 2017) is next year's
    return ANCHOR.year + (month < ANCHOR.month)


def _bounds(y, month, part):
    s = datetime(y, month, 1)
    e = datetime(y + 1, 1, 1) if month == 12 else datetime(y, month + 1, 1)
    w = (e - s) / 3
    return {"debut": (s, s + w),
            "milieu": (s + w, s + 2 * w),
            "fin": (s + 2 * w, e)}[part]


def _part_year(month, part):
    # ruling 1 (26 November 2026): a part of a month is read as a span; in the
    # anchor's own month (June 2017) a third that ended at or before the anchor
    # is June 2018's (debut 1-11 June and milieu 11-21 June have ended; fin,
    # 21 June to 1 July, holds the anchor and stays 2017)
    y = _year(month)
    if month == ANCHOR.month and _bounds(y, month, part)[1] <= ANCHOR:
        y += 1
    return y


def _third(month, part):
    lo, hi = _bounds(_part_year(month, part), month, part)
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
    # ruling 1: in June 2017 debut and milieu have ended (2018) while fin holds
    # the anchor (2017), so the thirds are contiguous only within one year
    assert d_e == m_s                          # contiguous
    if _part_year(month, "milieu") == _part_year(month, "fin"):
        assert m_e == f_s
    else:
        assert m_e == AstroDate(f_s.year + 1, f_s.month, f_s.day)
    yd = _part_year(month, "debut")
    yf = _part_year(month, "fin")
    assert d_s == AstroDate(yd, month, 1)     # opens the month
    end = AstroDate(yf + 1, 1, 1) if month == 12 else AstroDate(yf, month + 1, 1)
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
    # (ruling 1: février has ended at the anchor, so it is February 2018,
    # also 28 days)
    assert start_end("début février") == (
        AstroDate(2018, 2, 1), AstroDate(2018, 2, 10, 8, 0))
    assert start_end("mi-février") == (
        AstroDate(2018, 2, 10, 8, 0), AstroDate(2018, 2, 19, 16, 0))
    assert start_end("fin février") == (
        AstroDate(2018, 2, 19, 16, 0), AstroDate(2018, 3, 1))


@pytest.mark.parametrize("text", ["début", "la fin", "le milieu"])
def test_bare_fuzzy_word_is_not_a_month_third(text):
    nomatch(text)
