"""Romance (es/fr/pt) solstice/equinox resolve to the global astronomical DAY.

Solstices and equinoxes are location-independent astronomical INSTANTS, so the
Spanish/French/Portuguese phrasings ("solsticio de verano", "solstice d'été",
"solstício de verão") must resolve to the SAME civil day English already
produces from the Meeus ch.27 machinery -- not to the three-month
meteorological season span.  The 2017 cardinal dates are the independently
computed golds shared with ``test/nl_corpus_en/test_nl_solstice_equinox.py``
(Mar equinox 03-20, Jun solstice 06-21, Sep equinox 09-22, Dec solstice
12-21).  Adding the ``solar_event`` construction must NOT weaken the plain
season reading, which stays a whole-season span.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan

# a fixed anchor PAST the June solstice, so a yearless "el solsticio de verano"
# prefers the NEXT (2018) occurrence -- exactly as a bare holiday does
ANCHOR = datetime(2017, 6, 27, 13, 4)

# 2017 cardinal instants (Meeus ch.27), independent of the parser
JUN_SOLSTICE = date(2017, 6, 21)
MAR_EQUINOX = date(2017, 3, 20)
SEP_EQUINOX = date(2017, 9, 22)
DEC_SOLSTICE = date(2017, 12, 21)


@pytest.mark.parametrize("lang,phrase,expected", [
    # summer solstice -> June solstice (northern hemisphere)
    ("es", "el solsticio de verano 2017", JUN_SOLSTICE),
    ("fr", "le solstice d'été 2017", JUN_SOLSTICE),
    ("pt", "o solstício de verão 2017", JUN_SOLSTICE),
    # spring equinox -> March equinox
    ("es", "el equinoccio de primavera 2017", MAR_EQUINOX),
    ("fr", "l'équinoxe de printemps 2017", MAR_EQUINOX),
    ("pt", "o equinócio de primavera 2017", MAR_EQUINOX),
    # autumn equinox -> September equinox
    ("es", "el equinoccio de otoño 2017", SEP_EQUINOX),
    ("fr", "l'équinoxe d'automne 2017", SEP_EQUINOX),
    ("pt", "o equinócio de outono 2017", SEP_EQUINOX),
    # winter solstice -> December solstice
    ("es", "el solsticio de invierno 2017", DEC_SOLSTICE),
    ("fr", "le solstice d'hiver 2017", DEC_SOLSTICE),
    ("pt", "o solstício de inverno 2017", DEC_SOLSTICE),
    # unaccented surfaces the tokenizer may see
    ("es", "el equinocio de primavera 2017", MAR_EQUINOX),
    ("fr", "equinoxe de printemps 2017", MAR_EQUINOX),
    ("pt", "solsticio de verao 2017", JUN_SOLSTICE),
])
def test_romance_solar_event_is_single_day(lang, phrase, expected):
    res = extract_timespan(phrase, lang, ANCHOR)
    assert res is not None, f"{lang}: {phrase!r} did not resolve"
    # a SINGLE civil day, matching the English/Meeus gold
    assert res.span.start.date() == expected
    assert res.span.end.date() == date.fromordinal(expected.toordinal() + 1)
    # the whole phrase is consumed -- no stranded event/connector words
    assert res.remainder == ""


@pytest.mark.parametrize("lang,phrase", [
    ("es", "el solsticio de verano"),
    ("fr", "le solstice d'été"),
    ("pt", "o solstício de verão"),
])
def test_romance_bare_solar_event_prefers_future(lang, phrase):
    # yearless, anchor past the 2017 June solstice -> the 2018 instant
    res = extract_timespan(phrase, lang, ANCHOR)
    assert res is not None
    assert res.span.start.date() == date(2018, 6, 21)
    assert res.span.end.date() == date(2018, 6, 22)
    assert res.remainder == ""


@pytest.mark.parametrize("lang,phrase", [
    ("es", "en verano"),
    ("fr", "en été"),
    ("pt", "no verão"),
])
def test_plain_season_still_returns_the_season_span(lang, phrase):
    # the bare season phrase must STILL be the three-month meteorological span,
    # never hijacked by the new solar_event construction
    res = extract_timespan(phrase, lang, ANCHOR)
    assert res is not None
    assert res.span.start.date() == date(2017, 6, 1)
    assert res.span.end.date() == date(2017, 9, 1)
