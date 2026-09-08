"""Croatian offsets counted with the bare half: "za pola sata" (in half an
hour), "prije pola sata" (half an hour ago).  "pola" is a quantifier, not a
cardinal -- the clock's "pola devet" (08:30) needs it kept out of the number
fold -- so the offset grammar binds it through its QUANT slot, as Slovak's
"za pol hodiny" and Czech's "za půl hodiny" do.

Wiktionary (en), "pola", Serbo-Croatian, "half [with genitive]": "pola sata
-- half an hour".

Anchor: Tuesday 2017-06-27 13:04; every value is anchor arithmetic.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,delta", [
    ("za pola sata", timedelta(minutes=30)),
    ("prije pola sata", timedelta(minutes=-30)),
])
def test_half_an_hour_offset(text, delta):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == "", f"{text!r} stranded {res.remainder!r}"
    assert res[0].start == ad(ANCHOR + delta)


def test_half_past_clock_is_untouched():
    """"pola devet" is the clock's half toward nine, not a half-hour count."""
    res = parse("pola devet")
    assert res is not None
    assert res[0].start == ad(ANCHOR.replace(hour=8, minute=30) + timedelta(days=1))
