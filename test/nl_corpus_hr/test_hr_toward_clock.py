"""Croatian bare-cardinal toward-hour spoken clock.

Colloquial Croatian names the coming hour with a bare cardinal, not an
ordinal: "pola devet" == half toward nine == 08:30 (counted toward nine),
mirroring the Continental-Germanic ``bare_half_to`` convention. Citations,
both with a worked numeric example naming the SAME hour ("half past one" ==
1:30):
  - en.wiktionary.org/wiki/pola#Serbo-Croatian: "pola tri -- 2:30" (half
    toward three == 2:30).
  - en.wiktionary.org/wiki/half_past, Translations table (headword "half
    past one" == 1:30): "Serbo-Croatian: pola dva (used with the following
    hour)" -- "dva" (two) is the COMING hour, confirming the direction.

Exact H:MM, hand-derived.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, start, nomatch


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("pola devet", 8, 30),   # half toward the ninth
    ("pola tri", 2, 30),     # Wiktionary worked example
    ("pola deset", 9, 30),
    ("pola jedan", 12, 30),  # half toward one -> 12:30 (toward_hour_12h wrap)
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


def test_half_toward_hour_is_thirty_minutes_before_the_plain_hour():
    # Adversarial direction pin: "pola devet" must be exactly 30 minutes
    # before "u devet" (9:00, an absolute literal, not read back from the
    # parser's own reading of "pola devet") -- a reversed reading would
    # instead land at 9:30, an hour past "u devet" in the wrong direction.
    half = start("pola devet")
    plain = _next_time(9, 0)
    assert start("u devet") == plain
    assert plain - half == timedelta(minutes=30)


def test_half_hour_duration_still_resolves():
    # The standalone duration idiom ("pola sata" -- half an hour) resolves
    # through the QUANT/quantifiers path, unaffected by the clock FRACTION
    # wiring above.
    got = extract_duration("pola sata", "hr")
    assert got is not None
    assert got[0] == timedelta(minutes=30)


def test_bare_fraction_without_hour_is_not_a_clock():
    nomatch("pola")  # bare half, no hour
