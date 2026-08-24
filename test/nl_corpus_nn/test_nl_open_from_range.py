"""Open-ended "from <year>" ranges in Norwegian Nynorsk.

A from-marker with no terminator opens a span that runs to the anchor,
exactly as the language's "since" frame does; the closed from-to range
keeps its own reading.
"""
from datetime import datetime

from ._corpus import ANCHOR, ad, parse


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_open_from_year_runs_to_the_anchor():
    (start, end), rem = _span_rem("frå 2010")
    assert (start, end) == (ad(datetime(2010, 1, 1)), ad(ANCHOR))
    assert rem == ""


def test_since_frame_opens_the_same_span():
    (start, end), rem = _span_rem("sidan 2010")
    assert (start, end) == (ad(datetime(2010, 1, 1)), ad(ANCHOR))
    assert rem == ""


def test_closed_from_to_range_is_unchanged():
    # both years included in full: 2010-01-01 .. 2021-01-01
    (start, end), rem = _span_rem("frå 2010 til 2020")
    assert (start, end) == (ad(datetime(2010, 1, 1)),
                            ad(datetime(2021, 1, 1)))
    assert rem == ""
