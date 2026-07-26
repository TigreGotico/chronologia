"""Czech "A az B" closed date-range frame.

"az" is the horni-mez (upper-bound) connector of a numeric or calendar range
("tri az ctyri dny", "3. az 10. cervence"); before this it was not a "to"
word, so "3. az 10. cervence" stranded "3. az" and collapsed onto the 10th.
The already-working "od ... do" frame must stay working.
"""
from ._corpus import parse, start_end, AstroDate


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_az_days():
    (s, e), rem = _span_rem("3. až 10. července")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert rem == ""


def test_az_other_month():
    (s, e), rem = _span_rem("5. až 12. srpna")
    assert (s, e) == (AstroDate(2017, 8, 5), AstroDate(2017, 8, 13))
    assert rem == ""


def test_od_do_frame_unchanged():
    assert start_end("od 3. do 10. července") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))


def test_single_date_is_not_a_range():
    assert start_end("10. července") == (
        AstroDate(2017, 7, 10), AstroDate(2017, 7, 11))
