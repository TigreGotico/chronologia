"""A counted offset in the -ko genitive before a daypart, and a digit hour
with the absolutive plural "-ak".

"duela 3 eguneko gaua" is the night of three days ago: "-ko atzizkia
adizlagunei eransten zaie eta izenlagunak eratortzen ditu", with "atzo ->
atzoko egunkaria" (Trask, "-Ko atzizkia euskaraz", Euskera XXX, pp.
168-169).  The offset names the day and the daypart names the band on it,
as "atzoko gaua" already does for yesterday.

"arratsaldeko 5ak" is five in the afternoon.  The hour takes the article and
the plural mark ("hirurak dira"), and the digit form carries the same suffix
("arratsaldeko 3etatik gaueko 12ak arte"): Euskaltzaindia, Araua 35,
"Orduak nola esan", decisions 1 and 6, p. 185.

Anchor 2017-06-27 13:04, a Tuesday.  Three days back is Saturday 24 June,
two days back Sunday 25 June.  17:00 is still ahead of 13:04, so it is today;
08:00 has passed, so it is tomorrow.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


@pytest.mark.parametrize("text,lo,hi", [
    ("duela 3 eguneko gaua", (24, 21), (25, 0)),
    ("duela 3 egun gauean", (24, 21), (25, 0)),
    ("duela 2 eguneko arratsaldea", (25, 12), (25, 19)),
])
def test_offset_day_takes_the_daypart_band(text, lo, hi):
    r = parse(text)
    assert r is not None, text
    assert r[0].start == ad(datetime(2017, 6, lo[0], lo[1], 0))
    assert r[0].end == ad(datetime(2017, 6, hi[0], hi[1], 0))
    assert r.remainder == ""


@pytest.mark.parametrize("text,day,hour,rest", [
    ("arratsaldeko 5ak", 27, 17, ""),
    ("gaur arratsaldeko 5ak", 27, 17, ""),
    ("goizeko 8ak", 28, 8, ""),
    ("bilera arratsaldeko 5ak", 27, 17, "bilera"),
])
def test_absolutive_digit_hour(text, day, hour, rest):
    r = parse(text)
    assert r is not None, text
    assert r[0].start == ad(datetime(2017, 6, day, hour, 0))
    assert r.remainder == rest


def test_offset_alone_keeps_the_anchor_clock():
    # class 1: a counted offset with no daypart keeps 13:04
    r = parse("duela 3 egun")
    assert r[0].start == ad(datetime(2017, 6, 24, 13, 4))
    assert r.remainder == ""


def test_a_bare_absolutive_digit_is_no_time():
    assert parse("5ak") is None
