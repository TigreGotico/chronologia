"""Relative offsets in both directions -- the West-Slavic centre of gravity.

"za N <unit>" shifts forward, "před N <unit>" shifts back; the sign is the
marker's declared direction, so a past phrase can never leak forward (the
bug class this family carried).  Expected values are independent Python date
arithmetic against the Tuesday 2017-06-27 13:04 anchor.  Unit nouns are given
in the case each preposition governs -- accusative/genitive after "za",
instrumental/locative after "před".
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, parse, nomatch


# -- days: forward (za) and back (před), digit ---------------------------

@pytest.mark.parametrize("n,form", [(1, "den"), (2, "dny"), (3, "dny"),
                                    (5, "dní"), (7, "dní"), (10, "dnů"),
                                    (21, "dní")])
def test_days_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "dnem"), (2, "dny"), (3, "dny"),
                                    (5, "dny"), (2, "dnech"), (10, "dny")])
def test_days_past(n, form):
    assert start(f"před {n} {form}") == ad(ANCHOR - timedelta(days=n))


# -- weeks ---------------------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "týden"), (2, "týdny"), (3, "týdny"),
                                    (5, "týdnů"), (8, "týdnů")])
def test_weeks_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "týdny"), (3, "týdny"), (5, "týdny")])
def test_weeks_past(n, form):
    assert start(f"před {n} {form}") == ad(ANCHOR - timedelta(weeks=n))


# -- months --------------------------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "měsíc"), (2, "měsíce"), (3, "měsíce"),
                                    (5, "měsíců"), (8, "měsíců"), (12, "měsíců")])
def test_months_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "měsíci"), (5, "měsíci"), (3, "měsíci")])
def test_months_past(n, form):
    assert start(f"před {n} {form}") == ad(ANCHOR - relativedelta(months=n))


# -- years: the "lety" instrumental plural (a legacy gap) ----------------

@pytest.mark.parametrize("n,form", [(1, "rok"), (2, "roky"), (3, "roky"),
                                    (5, "let"), (10, "let"), (20, "let")])
def test_years_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 20])
def test_years_past_lety(n):
    # "před N lety" -- instrumental plural, the exact legacy fold that failed
    assert start(f"před {n} lety") == ad(ANCHOR - relativedelta(years=n))


# -- sub-day: hours and minutes ------------------------------------------

@pytest.mark.parametrize("n,form", [(1, "hodinu"), (2, "hodiny"), (3, "hodiny"),
                                    (5, "hodin")])
def test_hours_future(n, form):
    assert start(f"za {n} {form}") == ad(ANCHOR + timedelta(hours=n))


@pytest.mark.parametrize("n", [5, 10, 15, 30, 45])
def test_minutes_future(n):
    assert start(f"za {n} minut") == ad(ANCHOR + timedelta(minutes=n))


@pytest.mark.parametrize("n", [10, 30, 45])
def test_minutes_past(n):
    assert start(f"před {n} minutami") == ad(ANCHOR - timedelta(minutes=n))


# -- spelled numbers fold the same as digits -----------------------------

@pytest.mark.parametrize("phrase,delta", [
    ("za pět dní", timedelta(days=5)),
    ("za tři týdny", timedelta(weeks=3)),
    ("za deset minut", timedelta(minutes=10)),
    ("za dvacet minut", timedelta(minutes=20)),
    ("za sedm dní", timedelta(days=7)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


# NOTE: oblique/declined numerals ("pěti", "dvěma" -- instrumental of 5/2,
# as Czech grammar demands after "před") are not folded: ovos_number_parser
# only reads the nominative surface.  Grammatical spelled-past offsets are an
# engine-side (number-model) gap; digit forms cover the past direction above.
def test_oblique_numeral_spelled_past_is_a_gap():
    # documents the boundary rather than asserting a wrong span
    assert parse("před pěti lety") is None


# -- named days ----------------------------------------------------------

@pytest.mark.parametrize("word,off", [("dnes", 0), ("zítra", 1), ("včera", -1),
                                      ("pozítří", 2), ("předevčírem", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


# -- weekday reference: příští / minulý / tento <weekday> ----------------
# anchor is a Tuesday (index 1); hand-derived.

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("příští pondělí", _MID + timedelta(days=6)),
    ("příští úterý", _MID + timedelta(days=7)),
    ("příští pátek", _MID + timedelta(days=3)),
    ("minulý pátek", _MID - timedelta(days=4)),
    ("minulé úterý", _MID - timedelta(days=7)),
    ("tento čtvrtek", _MID + timedelta(days=2)),
    ("tento pátek", _MID + timedelta(days=3)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


def test_offset_width_is_unit_wide():
    from ._corpus import span
    assert span("za 3 dny").width == timedelta(days=1)
    assert span("za 2 týdny").width == timedelta(weeks=1)


# adversarial: a bare unit with no direction marker is not an offset.
def test_offset_needs_marker():
    nomatch("pět dní")
    nomatch("dva týdny")
    assert parse("minut") is None
