"""Counted nouns across the three mutation bands a numeral imposes.

Two lenites the noun after it, three to six leave a consonant bare and prefix
h to a vowel, seven to ten eclipse.  For "bliain" (year) and "uair" (hour)
every band is spelled out in the noun's own dictionary entry, so all three
surfaces of each are read: "dhá bhliain", "trí bliana", "seacht mbliana";
"dhá uair", "cúig huaire", "seacht n-uaire".

Each case asserts the offset the phrase names, so a surface that failed to
match would not merely return nothing -- it would return the wrong number of
years.  The radical is pinned alongside every mutated form, because a
vocabulary that lost the radical while keeping the mutation would pass a
mutation-only table and still be broken.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, remainder, start


@pytest.mark.parametrize("text,n", [
    ("bliain ó shin", 1),
    ("dhá bhliain ó shin", 2),
    ("trí bliana ó shin", 3),
    ("ceithre bliana ó shin", 4),
    ("cúig bliana ó shin", 5),
    ("sé bliana ó shin", 6),
    ("seacht mbliana ó shin", 7),
    ("ocht mbliana ó shin", 8),
    ("naoi mbliana ó shin", 9),
    ("deich mbliana ó shin", 10),
])
def test_year_counted_across_the_three_bands(text, n):
    assert start(text) == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("text", [
    "dhá bhliain ó shin", "trí bliana ó shin", "seacht mbliana ó shin",
])
def test_counted_year_consumes_everything(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,n", [
    ("uair ó shin", 1),
    ("dhá uair ó shin", 2),
    ("trí huaire ó shin", 3),
    ("ceithre huaire ó shin", 4),
    ("cúig huaire ó shin", 5),
    ("sé huaire ó shin", 6),
    ("seacht n-uaire ó shin", 7),
    ("ocht n-uaire ó shin", 8),
    ("naoi n-uaire ó shin", 9),
    ("deich n-uaire ó shin", 10),
])
def test_hour_counted_across_the_three_bands(text, n):
    assert start(text) == ad(ANCHOR - timedelta(hours=n))


def test_lenited_year_is_not_the_bare_one():
    """The lenited and the bare counted surfaces must both be read AND must
    keep their own numerals: reading "dhá bhliain" as one year, or "trí
    bliana" as two, is the silent-wrong this pair exists to prevent."""
    assert start("dhá bhliain ó shin") != start("bliain ó shin")
    assert start("trí bliana ó shin") != start("dhá bhliain ó shin")


def test_eclipsed_year_is_seven_not_one():
    assert start("seacht mbliana ó shin") == ad(
        ANCHOR - relativedelta(years=7))


def test_h_prothesis_hour_is_not_the_radical_hour():
    assert start("cúig huaire ó shin") != start("uair ó shin")


@pytest.mark.parametrize("text,n", [
    ("lá ó shin", 1),
    ("trí lá ó shin", 3),
    ("seacht lá ó shin", 7),
])
def test_day_shows_no_written_mutation(text, n):
    """"lá" begins with a consonant the modern standard spells no lenition
    on, so the counted phrase keeps the radical in every band."""
    assert start(text) == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("text,n", [
    ("mí ó shin", 1),
    ("trí mhí ó shin", 3),
])
def test_month_lenites_after_a_numeral(text, n):
    assert start(text) == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("text,n", [
    ("seachtain ó shin", 1),
    ("trí seachtaine ó shin", 3),
    ("cúig seachtaine ó shin", 5),
])
def test_week_counted(text, n):
    assert start(text) == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("text,n", [
    ("nóiméad ó shin", 1),
    ("deich nóiméad ó shin", 10),
    ("fiche a cúig nóiméad ó shin", 25),
])
def test_minute_counted(text, n):
    assert start(text) == ad(ANCHOR - timedelta(minutes=n))


def test_hundred_years_stays_unmutated():
    """"céad bliain" (a hundred years) is attested with neither the numeral
    nor the noun mutated, against the general claim that a higher numeral
    lenites what follows it.  Only the attested surface is read."""
    assert start("céad bliain ó shin") == ad(ANCHOR - relativedelta(years=100))
