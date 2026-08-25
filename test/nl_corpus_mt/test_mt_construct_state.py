"""The construct state: a counted noun changes the shape of its numeral.

Maltese has two forms for each of the numbers two through ten.  The
free-standing form (tnejn, tlieta, erbgħa, ... għaxra) is what a speaker says
when the number stands alone; the attributive form (żewġ, tliet, erba', ...
għaxar) is what precedes the noun being counted, and it splits further into a
short form and a long ``-t`` form used before a noun whose onset is a
consonant cluster.  From eleven upward the counted noun reverts to the
SINGULAR behind an ``-il`` linker written onto the numeral.

Gold is arithmetic on the anchor: "N <unit> ilu" is the anchor less N of that
unit, computed here with :mod:`datetime` and :mod:`dateutil`, never read back
from the parser.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, remainder, start_end


# -- the attributive form, two through ten, over days/weeks/months/years ----

@pytest.mark.parametrize("text,days", [
    ("żewġ ġranet ilu", 2),
    ("tliet ġranet ilu", 3),
    ("erba' ġranet ilu", 4),
    ("ħames ġranet ilu", 5),
    ("sitt ġranet ilu", 6),
    ("seba' ġranet ilu", 7),
    ("tmien ġranet ilu", 8),
    ("disa' ġranet ilu", 9),
    ("għaxar ġranet ilu", 10),
])
def test_attributive_numeral_counts_days(text, days):
    back = ANCHOR - timedelta(days=days)
    assert start_end(text) == (ad(back), ad(back + timedelta(days=1)))


@pytest.mark.parametrize("text,weeks", [
    ("tliet ġimgħat ilu", 3),
    ("erba' ġimgħat ilu", 4),
    ("sitt ġimgħat ilu", 6),
    ("għaxar ġimgħat ilu", 10),
])
def test_attributive_numeral_counts_weeks(text, weeks):
    back = ANCHOR - timedelta(weeks=weeks)
    assert start_end(text) == (ad(back), ad(back + timedelta(weeks=1)))


@pytest.mark.parametrize("text,months", [
    ("tliet xhur ilu", 3),
    ("ħames xhur ilu", 5),
    ("seba' xhur ilu", 7),
    ("għaxar xhur ilu", 10),
])
def test_attributive_numeral_counts_months(text, months):
    back = ANCHOR - relativedelta(months=months)
    assert start_end(text) == (ad(back), ad(back + relativedelta(months=1)))


@pytest.mark.parametrize("text,years", [
    ("tliet snin ilu", 3),
    ("erba' snin ilu", 4),
    ("ħames snin ilu", 5),
    ("tmien snin ilu", 8),
    ("disa' snin ilu", 9),
])
def test_attributive_numeral_counts_years(text, years):
    back = ANCHOR - relativedelta(years=years)
    assert start_end(text) == (ad(back), ad(back + relativedelta(years=1)))


# -- the long -t form, before a consonant-cluster onset ---------------------
# "elef" (thousands) opens on a cluster, which is exactly the environment the
# long form is for, and it is the environment the numeral table itself spells
# out: tlitt elef, erbat elef, ħamest elef, ...

@pytest.mark.parametrize("text,minutes", [
    ("tlitt elef minuta ilu", 3000),
    ("erbat elef minuta ilu", 4000),
    ("ħamest elef minuta ilu", 5000),
    ("sitt elef minuta ilu", 6000),
    ("sebat elef minuta ilu", 7000),
    ("tmint elef minuta ilu", 8000),
    ("disat elef minuta ilu", 9000),
    ("għaxart elef minuta ilu", 10000),
])
def test_the_long_form_multiplies_a_cluster_initial_thousand(text, minutes):
    back = ANCHOR - timedelta(minutes=minutes)
    assert start_end(text) == (ad(back), ad(back + timedelta(minutes=1)))


def test_the_il_linker_is_transparent_inside_a_thousand():
    back = ANCHOR - timedelta(minutes=12000)
    assert start_end("tnax-il elf minuta ilu") == (
        ad(back), ad(back + timedelta(minutes=1)))


# -- eleven upward: the -il linker and a SINGULAR noun ----------------------

@pytest.mark.parametrize("text,days", [
    ("ħdax-il jum ilu", 11),
    ("tnax-il jum ilu", 12),
    ("tlettax-il jum ilu", 13),
    ("erbatax-il jum ilu", 14),
    ("ħmistax-il jum ilu", 15),
    ("sittax-il jum ilu", 16),
    ("sbatax-il jum ilu", 17),
    ("tmintax-il jum ilu", 18),
    ("dsatax-il jum ilu", 19),
])
def test_the_il_linker_counts_a_singular_noun(text, days):
    back = ANCHOR - timedelta(days=days)
    assert start_end(text) == (ad(back), ad(back + timedelta(days=1)))


@pytest.mark.parametrize("text,years", [
    ("ħdax-il sena ilu", 11),
    ("ħmistax-il sena ilu", 15),
    ("dsatax-il sena ilu", 19),
])
def test_the_il_linker_counts_a_singular_year(text, years):
    back = ANCHOR - relativedelta(years=years)
    assert start_end(text) == (ad(back), ad(back + relativedelta(years=1)))


def test_the_whole_counted_phrase_is_consumed():
    assert remainder("ħdax-il sena ilu") == ""
    assert remainder("għaxar ġranet ilu") == ""


# -- the compound tens: unit + u + tens -------------------------------------

@pytest.mark.parametrize("text,minutes", [
    ("wieħed u għoxrin minuta ilu", 21),
    ("ħamsa u għoxrin minuta ilu", 25),
    ("tnejn u tletin minuta ilu", 32),
    ("ħamsa u erbgħin minuta ilu", 45),
    ("tmienja u ħamsin minuta ilu", 58),
])
def test_the_tens_compound_reads_unit_first(text, minutes):
    back = ANCHOR - timedelta(minutes=minutes)
    assert start_end(text) == (ad(back), ad(back + timedelta(minutes=1)))


@pytest.mark.parametrize("text,years", [
    ("għoxrin sena ilu", 20),
    ("tletin sena ilu", 30),
    ("ħamsin sena ilu", 50),
    ("mitt sena ilu", 100),
    ("tliet mitt sena ilu", 300),
])
def test_a_bare_tens_or_hundred_counts_years(text, years):
    back = ANCHOR - relativedelta(years=years)
    assert start_end(text) == (ad(back), ad(back + relativedelta(years=1)))


def test_a_bare_scale_word_stands_for_one_of_itself():
    # "mitt sena" is a hundred years and "elf sena" a thousand: the scale word
    # carries its own count, with no numeral in front of it.
    back = ANCHOR - relativedelta(years=1000)
    assert start_end("elf sena ilu") == (
        ad(back), ad(back + relativedelta(years=1)))
