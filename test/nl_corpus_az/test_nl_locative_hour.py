# -*- coding: utf-8 -*-
"""Azerbaijani locative-case clock hour: "saat üçdə" = "at three o'clock".

Azerbaijani marks "at <hour>" with the locative case on the numeral,
harmonising for backness and preceding-consonant voicing (-tə/-ta/-də/-da).
The suffixed form is the everyday way to state a clock time (Azərbaycan
dilinin izahlı lüğəti, s.v. "saat").  Each hour is spelled with its own gold,
computed independently of the parser, and the bare "saat <digit>" form pins
the same instant so the suffix is the only variable.  Anchor: 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import parse

A = datetime(2017, 6, 27, 13, 4)

# hour -> locative-suffixed spelling (vowel harmony + voicing per hour).
_LOCATIVE = {
    1: "birdə", 2: "ikidə", 3: "üçdə", 4: "dörddə", 5: "beşdə",
    6: "altıda", 7: "yeddidə", 8: "səkkizdə", 9: "doqquzda", 10: "onda",
    11: "on birdə", 12: "on ikidə",
}


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_locative_hour_reads_as_hour(h, word):
    r = parse("saat " + word, A)
    assert r is not None, f"'saat {word}' did not parse"
    assert r[0].start.hour == h


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_locative_matches_bare_digit(h, word):
    # The locative spelling must resolve identically to the plain digit form.
    assert parse("saat " + word, A) == parse("saat %d" % h, A)


@pytest.mark.parametrize("h,word", sorted(_LOCATIVE.items()))
def test_morning_daypart_keeps_am_hour(h, word):
    # "səhər" (morning) scopes to the AM half; a 1..11 hour is unchanged and
    # 12 (twelve in the morning) is midnight, i.e. 00:00 in 24h form.
    r = parse("səhər saat " + word, A)
    assert r is not None
    assert r[0].start.hour == (h % 12)
