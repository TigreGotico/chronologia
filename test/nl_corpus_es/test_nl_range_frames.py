"""Spanish "entre A y B" closed date-range frame, with articles.

"entre"/"y" were already the between/and connectors, but a bare range day
written with its article ("entre el 3 y el 10 de julio") left the left
endpoint as "el 3", which is not a lone numeral and does not resolve on its
own, so the shared-month borrow never fired and the range collapsed onto the
10th. The article carries no date and must not survive into the remainder;
the already-working "del ... al" and article-less "entre" frames must stay
working.
"""
from ._corpus import parse, start_end, AstroDate


def _span_rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return (r[0].start, r[0].end), r[1]


def test_entre_with_articles():
    (s, e), rem = _span_rem("entre el 3 y el 10 de julio")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert rem == ""


def test_entre_natural_sentence():
    (s, e), rem = _span_rem("las vacaciones son entre el 3 y el 10 de julio")
    assert (s, e) == (AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert rem == "las vacaciones son"


def test_working_frames_unchanged():
    assert start_end("entre 3 y 10 de julio") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert start_end("entre el 3 de julio y el 10 de julio") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))
    assert start_end("del 3 al 10 de julio") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 11))


def test_single_dated_day_with_article_unchanged():
    assert start_end("el 10 de julio") == (
        AstroDate(2017, 7, 10), AstroDate(2017, 7, 11))
