# -*- coding: utf-8 -*-
"""Italian day-part of an *explicit* referent: "la mattina del 25 dicembre",
"il pomeriggio del 5 luglio", "la sera di domani", "la mattina di lunedì".

The CLDR-``it`` bands (notte [00,06), mattina [06,12), pomeriggio [12,18),
sera [18,24)) are laid over the resolved referent day rather than over the
anchor day. Referent resolution is the ordinary next-occurrence rule
(anchor Tue 2017-06-27): a calendar date on/after the anchor, "domani" =
2017-06-28, the next named weekday, etc. Bands and referents are asserted by
hand; the parser is never consulted for the gold.
"""
import pytest

from ._corpus import start_end, AstroDate

# (text, referent-date y,m,d, band-start-hour, band-end-hour[, end-day-delta])
_CASES = [
    ("la mattina del 5 luglio", (2017, 7, 5), 6, 12),
    ("il pomeriggio del 5 luglio", (2017, 7, 5), 12, 18),
    ("la sera del 10 agosto", (2017, 8, 10), 18, 24),
    ("la notte del 1 gennaio", (2018, 1, 1), 0, 6),
    ("la mattina del 25 dicembre", (2017, 12, 25), 6, 12),
    ("il pomeriggio del 25 dicembre", (2017, 12, 25), 12, 18),
    ("la mattina del 3 marzo", (2018, 3, 3), 6, 12),
    # relative / weekday referents
    ("la sera di domani", (2017, 6, 28), 18, 24),
    ("la mattina di lunedì", (2017, 7, 3), 6, 12),  # next Monday after Tue 27
]


def _band(y, m, d, sh, eh):
    start = AstroDate(y, m, d, sh % 24, 0)
    if eh == 24:
        end = AstroDate(y, m, d) + __import__("datetime").timedelta(days=1)
    else:
        end = AstroDate(y, m, d, eh, 0)
    return start, end


@pytest.mark.parametrize("text,ymd,sh,eh", _CASES)
def test_daypart_of_date(text, ymd, sh, eh):
    assert start_end(text) == _band(*ymd, sh, eh)
