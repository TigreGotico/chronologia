"""French relative phrases: "dans N unites", "il y a N unites",
prochain/dernier weekdays, named days, and idiomatic compounds.

Expected values come from independent Python arithmetic against the Tuesday
2017-06-27 13:04 anchor.  ``relative_offset`` shifts the whole anchor and
keeps its time-of-day; ``named_day`` / ``weekday_ref`` land on midnight.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch, span


_NW = {1: "un", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq", 6: "six",
       7: "sept", 8: "huit", 9: "neuf", 10: "dix", 12: "douze",
       20: "vingt", 30: "trente"}


def _day_cases():
    out = []
    for n in (1, 2, 3, 5, 10, 20, 30):
        out.append((f"il y a {n} jours", ANCHOR - timedelta(days=n)))
        out.append((f"dans {n} jours", ANCHOR + timedelta(days=n)))
        if n != 1:
            out.append((f"dans {_NW[n]} jours", ANCHOR + timedelta(days=n)))
            out.append((f"il y a {_NW[n]} jours", ANCHOR - timedelta(days=n)))
    return out


def _week_cases():
    out = []
    for n in (2, 3, 4, 6):
        out.append((f"il y a {n} semaines", ANCHOR - timedelta(weeks=n)))
        out.append((f"dans {n} semaines", ANCHOR + timedelta(weeks=n)))
        out.append((f"dans {_NW[n]} semaines", ANCHOR + timedelta(weeks=n)))
    return out


def _month_cases():
    out = []
    for n in (1, 2, 3, 6, 8, 12):
        out.append((f"il y a {n} mois", ANCHOR - relativedelta(months=n)))
        out.append((f"dans {n} mois", ANCHOR + relativedelta(months=n)))
    return out


def _year_cases():
    out = []
    for n in (1, 2, 3, 5, 10, 20):
        out.append((f"il y a {n} ans", ANCHOR - relativedelta(years=n)))
        out.append((f"dans {n} ans", ANCHOR + relativedelta(years=n)))
    return out


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_relative_offset(text, expected):
    assert start(text) == ad(expected)


# -- sub-day offsets keep the anchor time-of-day --------------------------

@pytest.mark.parametrize("text,delta", [
    ("dans 3 heures", timedelta(hours=3)),
    ("dans deux heures", timedelta(hours=2)),
    ("dans 10 minutes", timedelta(minutes=10)),
    ("il y a 3 heures", timedelta(hours=-3)),
    ("il y a 30 minutes", timedelta(minutes=-30)),
])
def test_subday_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


# -- named days (day-wide, midnight) --------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("aujourd'hui", ANCHOR.replace(hour=0, minute=0)),
    ("demain", (ANCHOR + timedelta(days=1)).replace(hour=0, minute=0)),
    ("hier", (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0)),
    ("après-demain", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("avant-hier", (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0)),
])
def test_named_day(text, expected):
    assert start(text) == ad(expected)


def test_named_day_in_sentence():
    assert start("que s'est-il passé hier") == ad(
        (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0))
    assert start("le match d'avant-hier") == ad(
        (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0))


# -- weekday_ref: <weekday> prochain / dernier ----------------------------

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("lundi prochain", _MID + timedelta(days=6)),
    ("mardi prochain", _MID + timedelta(days=7)),
    ("mercredi prochain", _MID + timedelta(days=1)),
    ("jeudi prochain", _MID + timedelta(days=2)),
    ("vendredi prochain", _MID + timedelta(days=3)),
    ("samedi prochain", _MID + timedelta(days=4)),
    ("dimanche prochain", _MID + timedelta(days=5)),
    ("lundi dernier", _MID - timedelta(days=1)),
    ("mardi dernier", _MID - timedelta(days=7)),
    ("mercredi dernier", _MID - timedelta(days=6)),
    ("vendredi dernier", _MID - timedelta(days=4)),
    ("samedi dernier", _MID - timedelta(days=3)),
    ("dimanche dernier", _MID - timedelta(days=2)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


# -- referential widths ---------------------------------------------------

def test_named_day_is_day_wide():
    assert span("demain").width == timedelta(days=1)


def test_days_offset_is_day_wide():
    assert span("dans 3 jours").width == timedelta(days=1)


def test_weeks_offset_is_week_wide():
    assert span("dans 2 semaines").width == timedelta(weeks=1)


# -- idiomatic compounds --------------------------------------------------

@pytest.mark.parametrize("text,delta", [
    ("dans une quinzaine", timedelta(weeks=2)),
    ("il y a une quinzaine", timedelta(weeks=-2)),
])
def test_quinzaine(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("dans une semaine", timedelta(weeks=1)),
    ("il y a une semaine", timedelta(weeks=-1)),
    ("dans un mois", relativedelta(months=1)),
    ("il y a un an", relativedelta(years=-1)),
])
def test_indefinite_one(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,days", [
    ("il y a quelques jours", -3),
    ("dans quelques jours", 3),
])
def test_quantifier(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


# -- symmetry: dans N vs il y a N -----------------------------------------

def test_symmetry():
    fut = start("dans 2 semaines")
    past = start("il y a 2 semaines")
    assert (fut - past) == timedelta(days=28)


# -- adversarial ----------------------------------------------------------

def test_marker_without_offset_is_not_a_date():
    nomatch("il y a du monde")


def test_bare_unit_is_not_an_offset():
    nomatch("quinzaine")
    nomatch("azerty qwerty")
    nomatch("")
