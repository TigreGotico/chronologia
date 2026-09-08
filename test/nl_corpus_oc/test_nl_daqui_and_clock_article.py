"""Occitan future offsets with d'aquí / d'aicí, the article-led clock, and
"en N <unit>" as a length rather than a date.

Anchor: Tuesday 2017-06-27 13:04. Every expected value is arithmetic on the
anchor, never the engine's own output.

"d'aquí (a)" and "d'aicí (a)" front a future offset the way "dins" does:
oc.wiktionary s.v. "lèu" glosses it "dins un temps cort, d'aicí a pauc,
d'aquí un moment", and s.v. "aicí" lists "d'aicí a lèu", "d'aicí a pauc",
"d'aicí lèu", "d'aicí pauc" side by side, so the "a" is optional.

"en N jorns" is NOT a future time.  A native speaker, reviewing the legacy
Occitan extractor (OpenVoiceOS/ovos-date-parser#300): "'en 5 jorns' doesn't
mean 'in 5 days', it indicates a duration not a futur time."  oc.wikipedia,
"Titan (luna)": "orbita a l'entorn de Saturne en 15 jorns e 22 oras".

The article-led clock "a las 8 e mièja" carries the feminine plural article
in the at-slot, as in Catalan and Spanish; the elliptical "es las dètz manca
un quart" is written out on oc.wikipedia, "Auvernhat" (section on telling
the time).

"genier" is the provençau and vivaroaupenc spelling of "genièr",
oc.wiktionary s.v. "genièr", "Variantas dialectalas".
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, nomatch, parse


def _offset(text, delta, grain):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == "", f"{text!r} stranded {res.remainder!r}"
    assert res[0].start == ad(ANCHOR + delta)
    assert res[0].end == ad(ANCHOR + delta + grain)


@pytest.mark.parametrize("marker", ["d'aquí", "d'aquí a", "d'aicí", "d'aicí a",
                                    "dins"])
def test_future_offset_markers_agree(marker):
    _offset(f"{marker} 5 jorns", timedelta(days=5), timedelta(days=1))


@pytest.mark.parametrize("text,delta,grain", [
    ("d'aquí 15 segondas", timedelta(seconds=15), timedelta(seconds=1)),
    ("d'aquí 120 segondas", timedelta(seconds=120), timedelta(seconds=1)),
    ("d'aquí 1 minuta", timedelta(minutes=1), timedelta(minutes=1)),
    ("d'aquí 15 minutas", timedelta(minutes=15), timedelta(minutes=1)),
    ("d'aquí 90 minutas", timedelta(minutes=90), timedelta(minutes=1)),
    ("d'aquí una ora", timedelta(hours=1), timedelta(hours=1)),
    ("d'aicí a 15 minutas", timedelta(minutes=15), timedelta(minutes=1)),
])
def test_future_offset_value(text, delta, grain):
    _offset(text, delta, grain)


def test_half_an_hour_ahead():
    res = parse("d'aquí mièja ora")
    assert res is not None and res.remainder == ""
    assert res[0].start == ad(ANCHOR + timedelta(minutes=30))


@pytest.mark.parametrize("text,length", [
    ("en 5 jorns", timedelta(days=5)),
    ("en 2 setmanas", timedelta(weeks=2)),
    ("en 5 setmanas", timedelta(weeks=5)),
    ("en 10 minutas", timedelta(minutes=10)),
    ("en 5 segondas", timedelta(seconds=5)),
])
def test_en_names_a_length_not_a_date(text, length):
    nomatch(text)
    got = extract_duration(text, "oc")
    assert got is not None
    assert got.duration == length
    assert got.remainder == "en"


def test_en_with_a_clock_does_not_move_the_day():
    """The clock is real; the "en 2 jorns" before it is a length and must not
    push the date two days out."""
    res = parse("en 2 jorns a las 15")
    assert res is not None
    assert res[0].start == ad(ANCHOR.replace(hour=15, minute=0))
    assert "en 2 jorns" in res.remainder


def _next(h, m):
    cand = ANCHOR.replace(hour=h, minute=m, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,m", [
    ("a las 8 e mièja", 8, 30),
    ("a las 8 e quart", 8, 15),
    ("a las 8 manca un quart", 7, 45),
    ("las 8 manca un quart", 7, 45),
    ("a las 3 de l'aprèp-miègjorn", 15, 0),
    ("a las 8 e mièja del vespre", 20, 30),
])
def test_article_led_clock(text, h, m):
    res = parse(text)
    assert res is not None, f"{text!r} did not parse"
    assert res.remainder == ""
    assert res[0].start == _next(h, m)
    assert res[0].end == _next(h, m) + timedelta(minutes=1)


def test_the_two_fraction_directions_do_not_collapse():
    past, _ = parse("a las 8 e quart")
    to, _ = parse("a las 8 manca un quart")
    assert past.start - to.start == timedelta(minutes=30)


def test_genier_spelling_of_january():
    res = parse("1 de genier de 2119")
    assert res is not None and res.remainder == ""
    assert res[0].start == ad(datetime(2119, 1, 1))
    assert res[0].end == ad(datetime(2119, 1, 2))
