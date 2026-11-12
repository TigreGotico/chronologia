# -*- coding: utf-8 -*-
""""mañana" as the morning, and "ceo" after a day, ast.

DALLA s.v. "mañana, la": "Parte [del día] que va dende l'amanecida hasta'l
meudía"; s.v. "mañana" (adverb): "Nel día que sigue al de güei".  The noun
reading needs a demonstrative, an article, "de" (DALLA: "|| De mañana, na
parte del día que va dende l'amanecida hasta'l meudía") or "pela" (DALLA s.v.
"per": "Vémonos pela mañana").  DALLA s.v. "ceo": "Nes primeres hores del
día", so "mañana ceo" is tomorrow's morning.  Anchor 2017-06-27 13:04, a
Tuesday; the last Thursday is 22 June and the next Monday 3 July.  The band
is the library default morning, [06:00, 12:00).
"""
import pytest

from ._corpus import parse, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,ymd", [
    ("esta mañana", (2017, 6, 27)),
    ("mañana ceo", (2017, 6, 28)),
    ("mañana pela mañana", (2017, 6, 28)),
    ("mañana de mañana", (2017, 6, 28)),
    ("el llunes de mañana", (2017, 7, 3)),
    ("el xueves pasáu pela mañana", (2017, 6, 22)),
])
def test_the_morning_band(text, ymd):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(*ymd, 6), AstroDate(*ymd, 12))
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,ymd,rest", [
    ("mañana", (2017, 6, 28), ""),
    ("pasao mañana", (2017, 6, 29), ""),
    ("la reunión ta mañana", (2017, 6, 28), "la reunión ta"),
])
def test_the_bare_adverb_is_still_tomorrow(text, ymd, rest):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(*ymd), AstroDate(2017, 6, ymd[2] + 1))
    assert parse(text)[1] == rest


@pytest.mark.parametrize("text", ["ceo", "llegó ceo"])
def test_ceo_without_a_day_names_no_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["a partir de mañana", "el día de mañana"])
def test_de_manana_after_a_phrase_is_tomorrow(text):
    """After "a partir" or "el día", "mañana" is the adverb: "Nel día que
    sigue al de güei" (DALLA s.v. "mañana").  The answer is the whole of
    tomorrow, 28 June, not a morning that ended before 13:04."""
    s, e = start_end(text)
    assert (s, e) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))
