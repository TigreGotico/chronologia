# -*- coding: utf-8 -*-
"""Turkish locative-case clock hour: "saat üçte" = "at three o'clock".

Turkish marks "at <hour>" with the locative case on the numeral, harmonising
for backness and preceding-consonant voicing (-te/-ta/-de/-da).  The suffixed
form is the everyday way to state a clock time (TDK Güncel Türkçe Sözlük,
s.v. "saat").  Each hour is spelled with its own gold, computed independently
of the parser, and the bare "saat <digit>" form pins the same instant so the
suffix is the only variable.  Anchor: 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import parse

A = datetime(2017, 6, 27, 13, 4)


def _next_hour(h):
    """The next H:00 strictly after the anchor, computed without the parser."""
    cand = A.replace(hour=h, minute=0, second=0, microsecond=0)
    if cand <= A:
        cand += timedelta(days=1)
    return AstroDate(cand.year, cand.month, cand.day, h, 0)

# hour -> locative-suffixed spelling (vowel harmony + voicing per hour).
_LOCATIVE = {
    1: "birde", 2: "ikide", 3: "üçte", 4: "dörtte", 5: "beşte",
    6: "altıda", 7: "yedide", 8: "sekizde", 9: "dokuzda", 10: "onda",
    11: "on birde", 12: "on ikide",
}


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_locative_hour_reads_as_hour(h, word):
    r = parse("saat " + word, A)
    assert r is not None, f"'saat {word}' did not parse"
    assert r[0].start.hour == h


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_locative_hour_pins_the_next_occurrence(h, word):
    # A bare clock hour prefers the future, so an hour already past at 13:04
    # rolls to the following day.
    r = parse("saat " + word, A)
    assert r is not None
    assert r[0].start == _next_hour(h)


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_locative_matches_bare_digit(h, word):
    # The locative spelling must resolve identically to the plain digit form.
    assert parse("saat " + word, A) == parse("saat %d" % h, A)


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_morning_daypart_keeps_am_hour(h, word):
    # "sabah" (morning) scopes to the AM half; a 1..11 hour is unchanged and
    # 12 (twelve in the morning) is midnight, i.e. 00:00 in 24h form.
    r = parse("sabah saat " + word, A)
    assert r is not None
    assert r[0].start.hour == (h % 12)
