# -*- coding: utf-8 -*-
"""A day-offset ("N gün əvvəl") followed by the "saat H" clock reading.

"saat" is doubly loaded in Azerbaijani: it is both the HOUR unit word
(unit_hour.voc) and the clock's "at" preposition (marker_at.voc). Composed
with a leading digit ("saat 9") it reads as a clock; alone it is the bare
"hour" of an offset ("2 saat əvvəl" = 2 hours ago). Gold is independent
``timedelta``/``.replace(hour=...)`` arithmetic against the corpus anchor
(2017-06-27 13:04); see ``_corpus.ANCHOR``.

Decided semantics: "N gün əvvəl saat H" composes to a MINUTE-wide point at
hour H on the offset day (the same "clock pins a resolved day" composition
"dünən saat 9" already gets), remainder empty. "N gün əvvəl saat" with no
digit REFUSES the "saat" (strands it honestly, remainder='saat') rather than
guessing a phantom hour offset -- a genuine bare-hour offset ("bir saat
əvvəl", "2 saat əvvəl") never reaches this ambiguity because its own
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


@pytest.mark.parametrize("n,h", [(3, 9), (3, 3), (3, 12), (1, 0), (7, 23)])
def test_day_offset_composes_with_digit_clock(n, h):
    s = span(f"{n} gün əvvəl saat {h}")
    assert s.start == _hour_on_day_offset(n, h)
    assert s.end - s.start == timedelta(minutes=1)


def test_no_remainder_after_composition():
    r = parse("3 gün əvvəl saat 9")
    assert r.remainder == ""


def test_digit_never_stranded_regardless_of_hour_value():
    # Before the fix every one of these landed on the SAME wrong -3d-1h span
    # (the digit stranded as remainder) no matter what hour was named.
    s9 = start("3 gün əvvəl saat 9")
    s3 = start("3 gün əvvəl saat 3")
    s12 = start("3 gün əvvəl saat 12")
    assert s9.hour == 9 and s3.hour == 3 and s12.hour == 12
    assert s9.day == s3.day == s12.day == (ANCHOR - timedelta(days=3)).day


def test_bare_saat_with_no_digit_strands_honestly():
    r = parse("3 gün əvvəl saat")
    assert r.remainder == "saat"
    g = ANCHOR - timedelta(days=3)
    assert r.span.start == AstroDate(g.year, g.month, g.day, g.hour, g.minute)
    # the day-wide offset resolves on its own, un-narrowed by the stranded word
    assert r.span.end - r.span.start == timedelta(days=1)


def test_genuine_bare_hour_offset_unaffected():
    # "2 saat əvvəl" ("2 hours ago") is a genuine hour-unit offset: its "2"
    # is the primary relative_offset match's own NUM, not a trailing chunk,
    # so the r180 guard never touches it.
    s = start("2 saat əvvəl")
    assert s == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                          ANCHOR.hour - 2, ANCHOR.minute)


def test_bir_saat_evvel_unaffected():
    # "bir" ("one") folds to NUM=1 the same way, so "bir saat əvvəl" ("an
    # hour ago") is likewise a primary-match offset, untouched by the guard.
    s = start("bir saat əvvəl")
    assert s == AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day,
                          ANCHOR.hour - 1, ANCHOR.minute)


def test_dunen_saat_composition_unchanged():
    # The pre-existing working control this fix must not disturb: "dünən"
    # (yesterday) is a named_day, already composable with a trailing clock.
    s = start("dünən saat 9")
    d = ANCHOR - timedelta(days=1)
    assert s == AstroDate(d.year, d.month, d.day, 9, 0)


def test_bare_saat_clock_unchanged():
    # "saat 9" alone (no day offset) still resolves as the next occurrence
    # of 9:00 -- untouched by this fix (no relative_offset match at all).
    s = start("saat 9")
    assert s.hour == 9
