"""R119 sibling probe (de): a resolved PINPOINT clock start with a trailing
bare "für <duration>" extends the span's end, sharing the "recur_for"
marker vocabulary (``marker_recur_for.voc`` -> "für"/"fur") the recurrence
grammar already ships -- no new locale data needed.

Expected values are independently hand-computed against the anchor
(Tuesday 2017-06-27 13:04).
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, nomatch, parse, start_end


def test_dateless_clock_plus_hours_extends_end():
    # "um 9 Uhr" -- 9am has already passed today (anchor 13:04) -> rolls to
    # tomorrow; + 2h = 11am.
    s, e = start_end("um 9 Uhr für 2 Stunden")
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 11, 0)))


def test_clock_plus_minutes_extends_end():
    # "15:15" is still ahead of the 13:04 anchor -> today.
    r = parse("Besprechung um 15:15 für 45 Minuten")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 6, 27, 15, 15)),
                                          ad(datetime(2017, 6, 27, 16, 0)))
    assert r.remainder == "Besprechung um"


def test_bare_duration_alone_still_refused():
    nomatch("für 2 Stunden")
