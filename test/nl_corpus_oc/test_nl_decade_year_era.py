"""Occitan decade, ``de``-marked year, and the spelled-out BC era suffix.

Three surfaces oc.wikipedia writes but the locale could not read.  The
decade navbox on the "Ans 1980" page prints ``Ans 1950 | Ans 1960 | Ans
1970 | Ans 1980``, and running prose says "dins los ans 1980"; the year of
a calendar date is introduced with ``de`` exactly as in Catalan ("19 de
març de 2026"); and the era is spelled "abans nòstra èra" alongside the
abbreviated "abans Jèsus-Crist".

Expected values are plain arithmetic: a decade runs from its own January
1st to the next decade's, and a BC year N is the astronomical year 1 - N
(1500 BC is -1499).
"""
from datetime import datetime

import pytest

from ._corpus import AstroDate, ad, parse, span, start_end


@pytest.mark.parametrize("text", [
    "los ans 1980",
    "ans 1980",
    "las annadas 1980",
])
def test_decade_named_by_year_word_is_ten_years_wide(text):
    s, e = start_end(text)
    assert s == AstroDate(1980, 1, 1)
    assert e == AstroDate(1990, 1, 1)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("n", [1950, 1960, 1970, 1980, 1990, 2000, 2010])
def test_decade_navbox_series(n):
    """Every decade the oc.wikipedia navbox names spans its own ten years."""
    s, e = start_end("los ans %d" % n)
    assert s == AstroDate(n, 1, 1)
    assert e == AstroDate(n + 10, 1, 1)
    assert parse("los ans %d" % n)[1] == ""


def test_consecutive_decades_tile():
    _, earlier_end = start_end("los ans 1980")
    later_start, _ = start_end("los ans 1990")
    assert earlier_end == later_start == AstroDate(1990, 1, 1)


@pytest.mark.parametrize("text", [
    "15 de març de 2026",
    "19 de març de 2026",
])
def test_day_month_de_year(text):
    day = int(text.split()[0])
    s, e = start_end(text)
    assert s == AstroDate(2026, 3, day)
    assert e == AstroDate(2026, 3, day + 1)
    assert parse(text)[1] == ""


def test_month_de_year():
    s, e = start_end("març de 2026")
    assert s == AstroDate(2026, 3, 1)
    assert e == AstroDate(2026, 4, 1)
    assert parse("març de 2026")[1] == ""


def test_day_month_year_without_de_still_parses():
    """Control: the bare "15 de març 2026" shape must keep working."""
    s, e = start_end("15 de març 2026")
    assert s == AstroDate(2026, 3, 15)
    assert e == AstroDate(2026, 3, 16)
    assert parse("15 de març 2026")[1] == ""


@pytest.mark.parametrize("text", [
    "1500 abans nòstra èra",
    "1500 abans nostra era",
    "1500 abans Nòstra Èra",
])
def test_bc_era_spelled_out(text):
    s, e = start_end(text)
    assert s == AstroDate(-1499, 1, 1)
    assert e == AstroDate(-1498, 1, 1)
    assert parse(text)[1] == ""


def test_bc_era_abans_jesus_crist_control():
    """Control: the already-working two-word abbreviation is unchanged."""
    s, e = start_end("1500 abans Jèsus-Crist")
    assert s == AstroDate(-1499, 1, 1)
    assert e == AstroDate(-1498, 1, 1)
    assert parse("1500 abans Jèsus-Crist")[1] == ""


def test_bc_era_spelled_out_agrees_with_abbreviation():
    assert start_end("261 abans nòstra èra") == start_end("261 abans Jèsus-Crist")


def test_bc_era_year_is_one_less_than_the_bc_number():
    """44 BC is the astronomical year -43, not -44."""
    s, _ = start_end("44 abans nòstra èra")
    assert s == AstroDate(-43, 1, 1)


@pytest.mark.parametrize("text", [
    "l'an 1980",
    "an 1980",
    "l'annada 1980",
    "annada 1980",
])
def test_singular_year_word_names_one_year_not_the_decade(text):
    """``an``/``annada`` are singular: they frame a year, never a decade.

    ``era_year_ref.voc`` ships ``l'an`` and ``an`` as year-reference
    surfaces, so the decade construction must key on the plural alone --
    French reads ``l'an 1980`` as 1980 and ``les années 1980`` as the ten
    years, and Occitan says the same thing with the same contrast.
    """
    s, e = start_end(text)
    assert s == AstroDate(1980, 1, 1)
    assert e == AstroDate(1981, 1, 1)
    assert parse(text)[1] == ""


def test_singular_and_plural_year_words_disagree_by_nine_years():
    sing_start, sing_end = start_end("l'an 1980")
    plur_start, plur_end = start_end("los ans 1980")
    assert sing_start == plur_start == AstroDate(1980, 1, 1)
    assert sing_end == AstroDate(1981, 1, 1)
    assert plur_end == AstroDate(1990, 1, 1)


@pytest.mark.parametrize("text", [
    "ans 1914",
    "las annadas 1914",
    "los ans 1789",
])
def test_plural_year_word_with_a_non_ten_is_a_year_not_a_decade(text):
    """A decade opens on a whole ten, so 1914 stays a single year.

    "las annadas 1914-1918" are the war years, a run of years the range
    machinery reads; letting 1914 name a decade would round it to 1910.
    """
    n = int(text.split()[-1])
    s, e = start_end(text)
    assert s == AstroDate(n, 1, 1)
    assert e == AstroDate(n + 1, 1, 1)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", [
    "1500 de nòstra èra",
    "1500 de nostra era",
    "1500 de Nòstra Èra",
])
def test_ad_era_spelled_out(text):
    """The AD half of the spelled era pair, mirroring "abans nòstra èra"."""
    s, e = start_end(text)
    assert s == AstroDate(1500, 1, 1)
    assert e == AstroDate(1501, 1, 1)
    assert parse(text)[1] == ""


def test_ad_era_spelled_out_agrees_with_the_abbreviation():
    assert start_end("1500 de nòstra èra") == start_end("1500 aprèp Jèsus-Crist")


def test_ad_and_bc_eras_straddle_year_zero():
    ad_start, _ = start_end("1500 de nòstra èra")
    bc_start, _ = start_end("1500 abans nòstra èra")
    assert ad_start == AstroDate(1500, 1, 1)
    assert bc_start == AstroDate(-1499, 1, 1)


#: a Saturday, 13:04 -- late enough in 2026 that March 2026 is already past.
_LATE_2026 = datetime(2026, 6, 27, 13, 4)


@pytest.mark.parametrize("text", [
    "fins al 15 de març de 2028",
    "fins al 15 de març 2028",
])
def test_until_a_dated_year_keeps_the_range_open(text):
    """The year now binds, so "until 15 March 2028" runs from the anchor."""
    s = span(text, _LATE_2026)
    assert ad(s.start) == ad(_LATE_2026)
    assert s.end == AstroDate(2028, 3, 16)
    assert parse(text, _LATE_2026)[1] == ""


def test_until_a_dated_month_keeps_the_range_open():
    s = span("fins al març de 2028", _LATE_2026)
    assert ad(s.start) == ad(_LATE_2026)
    assert s.end == AstroDate(2028, 4, 1)
    assert parse("fins al març de 2028", _LATE_2026)[1] == ""


def test_since_a_dated_year_keeps_the_range_open():
    s = span("dempuèi lo 15 de març de 2020", _LATE_2026)
    assert s.start == AstroDate(2020, 3, 15)
    assert ad(s.end) == ad(_LATE_2026)


def test_dated_range_endpoints_both_take_their_year():
    s, e = start_end("del 15 de març de 2026 al 20 d'abril de 2026", _LATE_2026)
    assert s == AstroDate(2026, 3, 15)
    assert e == AstroDate(2026, 4, 21)
