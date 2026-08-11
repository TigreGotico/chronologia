"""R119 sibling probe (fr): a resolved PINPOINT clock start with a trailing
bare "pendant <duration>" extends the span's end, sharing the "recur_for"
marker vocabulary (``marker_recur_for.voc`` -> "pendant"/"pour") the
recurrence grammar already ships -- no new locale data needed.

Note: a bare "pendant 2 heures" (no OTHER clock cue) is not pinned as a
control here -- French "2 heures" is itself ambiguous with the clock_time
reading ("il est 2 heures" == "it's 2 o'clock"), so it already resolves to
a (wrong, pre-existing, out of R119's scope) clock reading on ``dev``
before this fix; this file only pins the genuine clock-start + duration
composition, which is unambiguous.

Expected values are independently hand-computed against the anchor
(Tuesday 2017-06-27 13:04).
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, parse, start_end


def test_dateless_clock_plus_hours_extends_end():
    # "a 9h" -- 9am has already passed today (anchor 13:04) -> rolls to
    # tomorrow; + 2h = 11am.
    s, e = start_end("a 9h pendant 2 heures")
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 11, 0)))


def test_clock_plus_minutes_extends_end():
    # "15h15" is still ahead of the 13:04 anchor -> today.
    r = parse("reunion a 15h15 pendant 45 minutes")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 6, 27, 15, 15)),
                                          ad(datetime(2017, 6, 27, 16, 0)))
    assert r.remainder == "reunion"
