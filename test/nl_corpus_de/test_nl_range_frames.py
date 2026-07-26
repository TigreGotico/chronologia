"""German "vom ... bis ..." closed date-range frame.

"vom" (the fused "von dem") is the ordinary range opener paired with "bis";
before this it was not in the from-lead vocabulary, so "vom 3. bis 10. Juli"
stranded "vom 3. bis" in the remainder and collapsed onto the 10th. The
already-working "zwischen ... und" and bare "bis" frames must stay working,
and a bare "vom <date>" (no "bis") must not fabricate a range.
"""
from ._corpus import parse, start_end, AstroDate


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_vom_bis_days():
    # 3 July .. 11 July (end-exclusive) == an 8-day span, anchored 2017
    (s, e), rem = _span_rem("vom 3. bis 10. Juli")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert rem == ""


def test_vom_bis_natural_sentence():
    # a subject before the frame does not disturb the span it reads
    (s, e), _rem = _span_rem("der Urlaub geht vom 3. bis 10. Juli")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))


def test_working_frames_unchanged():
    assert start_end("zwischen 3. und 10. Juli") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert start_end("3. bis 10. Juli") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))


def test_vom_without_bis_is_not_a_range():
    # a lone "vom <date>" names a single day, never an 8-day span
    assert start_end("vom 10. Juli") == (
        AstroDate(2017, 7, 10), AstroDate(2017, 7, 11))
