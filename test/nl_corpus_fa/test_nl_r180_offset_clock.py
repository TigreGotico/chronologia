# -*- coding: utf-8 -*-
"""A day-offset ("N روز پیش") followed by the "ساعت H" clock reading.

"ساعت" is doubly loaded in Persian: it is both the HOUR unit word
(unit_hour.voc) and the clock's "at" preposition (marker_at.voc). Composed
with a leading digit ("ساعت 3") it reads as a clock; alone it is the bare
"hour" of an offset ("2 ساعت پیش" = 2 hours ago). Gold is independent
``timedelta``/``.replace(hour=...)`` arithmetic against the corpus anchor
(2017-06-27 13:04); see ``_corpus.ANCHOR``.

Decided semantics: "N روز پیش ساعت H" composes to a MINUTE-wide point at
hour H on the offset day (the same "clock pins a resolved day" composition
"دیروز ساعت 9" already gets), remainder empty. "N روز پیش ساعت" with no digit
REFUSES the "ساعت" (strands it honestly, remainder='ساعت') rather than
guessing a phantom hour offset -- a genuine bare-hour offset ("یک ساعت پیش",
"2 ساعت پیش") never reaches this ambiguity because its own NUM/quantifier
sits in the SAME primary relative_offset match, not a trailing scan.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, span, start, parse


def _hour_on_day_offset(n, h):
    d = (ANCHOR - timedelta(days=n)).replace(hour=h, minute=0, second=0,
                                             microsecond=0)
    return AstroDate(d.year, d.month, d.day, d.hour, d.minute)


@pytest.mark.parametrize("n,h", [(3, 9), (3, 3), (3, 12), (1, 0), (5, 23)])
def test_day_offset_composes_with_digit_clock(n, h):
    s = span(f"{n} روز پیش ساعت {h}")
    assert s.start == _hour_on_day_offset(n, h)
    assert s.end - s.start == timedelta(minutes=1)


def test_no_remainder_after_composition():
    r = parse("3 روز پیش ساعت 3")
    assert r.remainder == ""


def test_digit_never_stranded_regardless_of_hour_value():
    # Before the fix every one of these landed on the SAME wrong -3d-1h span
    # (the digit stranded as remainder) no matter what hour was named.
    s9 = start("3 روز پیش ساعت 9")
    s3 = start("3 روز پیش ساعت 3")
    s12 = start("3 روز پیش ساعت 12")
    assert s9.hour == 9 and s3.hour == 3 and s12.hour == 12
    assert s9.day == s3.day == s12.day == (ANCHOR - timedelta(days=3)).day


def test_bare_saat_with_no_digit_strands_honestly():
    r = parse("3 روز پیش ساعت")
    assert r.remainder == "ساعت"
    g = ANCHOR - timedelta(days=3)
    assert r.span.start == AstroDate(g.year, g.month, g.day, g.hour, g.minute)
    assert r.span.end - r.span.start == timedelta(days=1)


def test_genuine_bare_hour_offset_unaffected():
    # "2 ساعت پیش" ("2 hours ago") is a genuine hour-unit offset: its "2" is
    # the primary relative_offset match's own NUM, not a trailing chunk, so
    # the r180 guard never touches it.
    s = start("2 ساعت پیش")
    assert s == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                          ANCHOR.hour - 2, ANCHOR.minute)


def test_yek_saat_pish_unaffected():
    s = start("یک ساعت پیش")
    assert s == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                          ANCHOR.hour - 1, ANCHOR.minute)


def test_diruz_saat_composition_unchanged():
    # The pre-existing working control this fix must not disturb: "دیروز"
    # (yesterday) is a named_day, already composable with a trailing clock.
    s = start("دیروز ساعت 9")
    d = ANCHOR - timedelta(days=1)
    assert s == AstroDate(d.year, d.month, d.day, 9, 0)
