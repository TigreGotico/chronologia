# -*- coding: utf-8 -*-
"""A day-offset ("N gün önce") followed by the "saat H" clock reading.

"saat" is doubly loaded in Turkish: it is both the HOUR unit word
(unit_hour.voc) and the clock's "at" preposition (marker_at.voc). Composed
with a leading digit ("saat 3") it reads as a clock; alone it is the bare
"hour" of an offset ("2 saat önce" = 2 hours ago). Gold is independent
``timedelta``/``.replace(hour=...)`` arithmetic against the corpus anchor
(2026-07-15 12:00, a Wednesday); see ``_corpus.ANCHOR``.

Decided semantics: "N gün önce saat H" composes to a MINUTE-wide point at
hour H on the offset day (the same "clock pins a resolved day" composition
"dün saat 9" already gets), remainder empty. "N gün önce saat" with no digit
REFUSES the "saat" (strands it honestly, remainder='saat') rather than
guessing a phantom hour offset -- a genuine bare-hour offset ("bir saat
önce", "2 saat önce") never reaches this ambiguity because its own
NUM/quantifier sits in the SAME primary relative_offset match, not a
trailing scan.
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
    s = span(f"{n} gün önce saat {h}")
    assert s.start == _hour_on_day_offset(n, h)
    assert s.end - s.start == timedelta(minutes=1)


def test_no_remainder_after_composition():
    r = parse("3 gün önce saat 3")
    assert r.remainder == ""


def test_digit_never_stranded_regardless_of_hour_value():
    # Before the fix every one of these landed on the SAME wrong -3d-1h span
    # (the digit stranded as remainder) no matter what hour was named.
    s9 = start("3 gün önce saat 9")
    s3 = start("3 gün önce saat 3")
    s12 = start("3 gün önce saat 12")
    assert s9.hour == 9 and s3.hour == 3 and s12.hour == 12
    assert s9.day == s3.day == s12.day == (ANCHOR - timedelta(days=3)).day


def test_bare_saat_with_no_digit_strands_honestly():
    r = parse("3 gün önce saat")
    assert r.remainder == "saat"
    g = ANCHOR - timedelta(days=3)
    assert r.span.start == AstroDate(g.year, g.month, g.day, g.hour, g.minute)
    assert r.span.end - r.span.start == timedelta(days=1)


def test_genuine_bare_hour_offset_unaffected():
    # "2 saat önce" ("2 hours ago") is a genuine hour-unit offset: its "2"
    # is the primary relative_offset match's own NUM, not a trailing chunk,
    # so the r180 guard never touches it.
    s = start("2 saat önce")
    assert s == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                          ANCHOR.hour - 2, ANCHOR.minute)


def test_bir_saat_once_unaffected():
    s = start("bir saat önce")
    assert s == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                          ANCHOR.hour - 1, ANCHOR.minute)


def test_dun_saat_composition_unchanged():
    # The pre-existing working control this fix must not disturb: "dün"
    # (yesterday) is a named_day, already composable with a trailing clock.
    s = start("dün saat 9")
    d = ANCHOR - timedelta(days=1)
    assert s == AstroDate(d.year, d.month, d.day, 9, 0)
