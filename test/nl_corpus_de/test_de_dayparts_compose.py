# -*- coding: utf-8 -*-
"""German day-part composition beyond the base bands.

This complements ``test_nl_daypart.py`` (which pins heute/gestern/morgen x
Vormittag/Nachmittag/Abend) with:

* the bare *-s adverbs "vormittags / nachmittags / abends / nachts", which
  resolve on the anchor day;
* composition with vorgestern (-2) and uebermorgen (+2);
* "Mittag", which is the noon *instant* (a minute-wide span at 12:00), not a
  band, so "heute Mittag" / "morgen Mittag" land 12:00-12:01.

CLDR 47 ``de`` bands (chronologia.dayparts): Nacht [00:00,05:00), Vormittag
[10:00,12:00), Nachmittag [13:00,18:00), Abend [18:00,24:00). Oracle is fixed
arithmetic off the anchor day 2017-06-27. No new duplicates of the base file.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_ANCHOR_DAY = date(2017, 6, 27)

# band -> (start_h, end_h) with end_h == 24 meaning midnight next day
_BAND = {
    "nacht": (0, 5),
    "vormittag": (10, 12),
    "nachmittag": (13, 18),
    "abend": (18, 24),
}


def _band_span(offset, band):
    d = _ANCHOR_DAY + timedelta(days=offset)
    h0, h1 = _BAND[band]
    start = AstroDate(d.year, d.month, d.day, h0, 0)
    if h1 == 24:
        nxt = d + timedelta(days=1)
        end = AstroDate(nxt.year, nxt.month, nxt.day)
    else:
        end = AstroDate(d.year, d.month, d.day, h1, 0)
    return start, end


_DAYWORD = {"vorgestern": -2, "gestern": -1, "heute": 0, "übermorgen": 2}

# composed day-word + band, avoiding the pairs already in test_nl_daypart.py
_COMPOSED = [
    ("vorgestern abend", -2, "abend"),
    ("vorgestern nachmittag", -2, "nachmittag"),
    ("vorgestern nacht", -2, "nacht"),
    ("übermorgen abend", 2, "abend"),
    ("übermorgen nachmittag", 2, "nachmittag"),
    ("übermorgen vormittag", 2, "vormittag"),
    ("gestern vormittag", -1, "vormittag"),
    ("heute nacht", 0, "nacht"),
    ("morgen nachmittag", 1, "nachmittag"),
    ("morgen nacht", 1, "nacht"),
]


@pytest.mark.parametrize("text,offset,band", _COMPOSED)
def test_composed_daypart(text, offset, band):
    s, e = _band_span(offset, band)
    sp = span(text)
    assert (sp.start, sp.end) == (s, e), f"{text!r} -> {sp}"


# bare *-s adverbs -- resolve on the anchor day
@pytest.mark.parametrize("text,band", [
    ("vormittags", "vormittag"),
    ("nachmittags", "nachmittag"),
    ("abends", "abend"),
    ("nachts", "nacht"),
])
def test_bare_adverb(text, band):
    s, e = _band_span(0, band)
    sp = span(text)
    assert (sp.start, sp.end) == (s, e), f"{text!r} -> {sp}"


# "Mittag" is the noon instant, minute-wide -- not a band
@pytest.mark.parametrize("text,day", [
    ("heute mittag", date(2017, 6, 27)),
    ("morgen mittag", date(2017, 6, 28)),
])
def test_mittag_is_noon_instant(text, day):
    sp = span(text)
    assert sp.start == AstroDate(day.year, day.month, day.day, 12, 0)
    assert sp.end == AstroDate(day.year, day.month, day.day, 12, 1)
