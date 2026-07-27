"""English/Scottish quarter-days and traditional term-days.

These are FIXED-DATE traditional holidays of the English legal/church calendar
(the four English quarter-days, the four Scottish term-days, and a couple of
adjacent feasts), resolved through the same WELL_KNOWN fixed-date registry that
already carries Christmas.  Each fixed date is hand-verified against the standard
English legal / General Roman Calendar dates:

    Lady Day       = 25 Mar  (Feast of the Annunciation; English quarter-day and
                              the civil New Year pre-1752)
    Midsummer Day  = 24 Jun  (Nativity of St John the Baptist; quarter-day)
    Michaelmas     = 29 Sep  (Feast of St Michael; quarter-day + legal term)
    Christmas      = 25 Dec  (quarter-day; already carried as ``christmas``)
    Candlemas      =  2 Feb  (Presentation; Scottish term-day)
    Lammas Day     =  1 Aug  (Loaf-mass; Scottish term-day)
    Martinmas      = 11 Nov  (St Martin; Scottish term-day)

Twelfth Night (5 Jan) is deliberately NOT added: it is pinned elsewhere as a
proper noun that must resolve to None (not a daypart "night"), and Epiphany
itself (6 Jan) is already carried.

The "bare" rule (inherited from the well-known machinery) is *next occurrence on
or after the 2017-06-27 anchor* -- a feast already past in 2017 rolls to 2018.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch


def _day(y, m, d):
    return AstroDate(y, m, d), AstroDate(y, m, d + 1) if d < 28 else None


# -- named + explicit year -> the fixed date -------------------------------
_WITH_YEAR = [
    ("Lady Day 1750", (1750, 3, 25)),
    ("Midsummer Day 1750", (1750, 6, 24)),
    ("Midsummer 1750", (1750, 6, 24)),
    ("Michaelmas 1751", (1751, 9, 29)),
    ("Michaelmas Day 1751", (1751, 9, 29)),
    ("Candlemas 1750", (1750, 2, 2)),
    ("Lammas 1750", (1750, 8, 1)),
    ("Lammas Day 1750", (1750, 8, 1)),
    ("Martinmas 1750", (1750, 11, 11)),
    # Christmas quarter-day already resolves; pin it stays 25 Dec.
    ("Christmas Day 1750", (1750, 12, 25)),
]


@pytest.mark.parametrize("text,ymd", _WITH_YEAR)
def test_named_year_fixed_date(text, ymd):
    y, m, d = ymd
    assert start(text) == AstroDate(y, m, d)


# -- bare name -> next occurrence on or after the 2017-06-27 anchor ---------
_BARE = [
    ("Michaelmas", (2017, 9, 29)),      # 29 Sep still ahead -> this year
    ("Lady Day", (2018, 3, 25)),        # 25 Mar already past -> next year
    ("Midsummer", (2018, 6, 24)),       # 24 Jun < 27 Jun -> next year
    ("Midsummer Day", (2018, 6, 24)),
    ("Candlemas", (2018, 2, 2)),        # 2 Feb past -> next year
    ("Lammas", (2017, 8, 1)),           # 1 Aug ahead -> this year
    ("Martinmas", (2017, 11, 11)),      # 11 Nov ahead -> this year
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_prefers_future(text, ymd):
    y, m, d = ymd
    assert start(text) == AstroDate(y, m, d)


# -- collision regression: the embedded "Day"/weekday tokens are unaffected -
def test_bare_day_tokens_unchanged():
    # "day" alone does not parse (unchanged from before quarter-days existed).
    nomatch("day")
    nomatch("a day")
    # "today" and weekdays keep their exact readings.
    assert start("today") == AstroDate(2017, 6, 27)
    assert start("Monday") == AstroDate(2017, 7, 3)
    assert start("next Monday") == AstroDate(2017, 7, 3)
    # Twelfth Night stays a proper noun with no holiday reading (deferred).
    nomatch("Twelfth Night")


def test_feast_surface_wins_longest_match():
    # "Michaelmas Day" must resolve to 29 Sep, not decay to a bare "day".
    assert start("Michaelmas Day 1751") == AstroDate(1751, 9, 29)
    assert start("Lammas Day 1750") == AstroDate(1750, 8, 1)
