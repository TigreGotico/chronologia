# -*- coding: utf-8 -*-
"""R119 sibling probe (es): a resolved PINPOINT clock start with a trailing
bare "durante <duration>" extends the span's end, sharing the "recur_for"
marker vocabulary (``marker_recur_for.voc`` -> "durante"/"por") the
recurrence grammar already ships -- no new locale data needed.

Expected values are independently hand-computed against the anchor
(Tuesday 2017-06-27 13:04).
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, nomatch, parse, start_end


def test_dateless_clock_plus_hours_extends_end():
    # "a las 9am" -- 9am has already passed today (anchor 13:04) -> rolls to
    # tomorrow; + 2h = 11am.
    s, e = start_end("a las 9am durante 2 horas")
    assert (s, e) == (ad(datetime(2017, 6, 28, 9, 0)),
                      ad(datetime(2017, 6, 28, 11, 0)))


def test_clock_plus_minutes_extends_end():
    # "3:15pm" (15:15) is still ahead of the 13:04 anchor -> today.
    r = parse("reunion a las 3:15pm durante 45 minutos")
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(datetime(2017, 6, 27, 15, 15)),
                                          ad(datetime(2017, 6, 27, 16, 0)))
    assert r.remainder == "reunion"


def test_bare_duration_alone_still_refused():
    nomatch("durante 2 horas")
