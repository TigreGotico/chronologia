# -*- coding: utf-8 -*-
"""sv: a spoken hour -- bare, or carrying a fractional/relative-minute
reading -- binds to a following "på <daypart>en" phrase as its MERIDIEM,
resolving to the pinpoint hour -- "atta pa kvallen" (eight in the evening)
is 20:00, "halv nio pa kvallen" (half past eight) is 20:30, not the whole
six-hour evening band with the fraction/hour word stranded in the
remainder.  The daypart words double as the MERIDIEM slot exactly as es "de
la tarde"/pt "da noite" already do (see their clock_meridiem_*.voc),
reusing chronologia/extract/resolver.py's existing MERIDIEM-shift
machinery, mirrored across clock_time's bare/FRACTION/FRACTION CLOCKDIR/
MINUTE CLOCKDIR sibling orders the same way chronologia/locale/en/lang.json
ships them for "half nine in the evening".

The MERIDIEM shift itself is a flat +12 (or no-op) on the spoken 1..12
hour, the same engine-wide convention es/pt/en already apply -- it does
NOT consult the day-part's own CLDR band, so the literal hour twelve
("tolv") is a pre-existing, locale-independent quirk: "tolv pa
formiddagen"/"tolv pa morgonen" read as midnight rather than the band's own
noon-adjacent reading, and "ett"/"fem pa kvallen" (both outside the kvall
band) still shift by the flat rule.  That quirk is out of scope here.

Anchor: Tuesday 2017-06-27 13:04, so an AM-side hour earlier than 13:04
rolls to tomorrow (the same "roll forward if already past" convention every
other sv clock reading already follows) while a PM-side hour later than
13:04 stays today.
"""
from datetime import datetime
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, ANCHOR


@pytest.mark.parametrize("text,dt", [
    ("åtta på kvällen", datetime(2017, 6, 27, 20, 0)),
    ("tre på eftermiddagen", datetime(2017, 6, 27, 15, 0)),
    ("sju på morgonen", datetime(2017, 6, 28, 7, 0)),
])
def test_hour_binds_to_daypart(text, dt):
    s = span(text)
    assert s.start == AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


@pytest.mark.parametrize("text,dt", [
    ("halv nio på kvällen", datetime(2017, 6, 27, 20, 30)),
    ("halv fyra på eftermiddagen", datetime(2017, 6, 27, 15, 30)),
    ("klockan halv nio på kvällen", datetime(2017, 6, 27, 20, 30)),
    ("kvart i nio på kvällen", datetime(2017, 6, 27, 20, 45)),
    ("fem i åtta på kvällen", datetime(2017, 6, 27, 19, 55)),
    ("tjugo över sju på kvällen", datetime(2017, 6, 27, 19, 20)),
])
def test_fractional_hour_binds_to_daypart(text, dt):
    """The FRACTION/FRACTION CLOCKDIR/MINUTE CLOCKDIR siblings of the bare
    HOUR-MERIDIEM order: without them "halv nio pa kvallen" strands "halv"
    in the remainder and returns the wrong half-hour (08:30 instead of
    20:30) -- the fraction, not the daypart, decides the minute."""
    s = span(text)
    assert s.start == AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


def test_bare_daypart_with_no_hour_stays_the_whole_band():
    """Adversarial: a day-part word with no spoken hour must NOT collapse to
    a point -- it still names the whole six-hour band, proving the new
    MERIDIEM orders bind only when an hour is actually present."""
    s = span("på kvällen")
    assert s.start == AstroDate(2017, 6, 27, 18, 0)
    assert s.end == AstroDate(2017, 6, 28, 0, 0)
