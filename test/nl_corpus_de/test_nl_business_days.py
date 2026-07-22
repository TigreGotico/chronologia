"""Werktage / Arbeitstage: "in N Werktagen", "der nächste Werktag",
"N Werktage nach Weihnachten".

Ein Werktag ist ein Wochentag, der weder Wochenende noch gesetzlicher
Feiertag der ``jurisdiction`` ist.  Ohne Jurisdiktion ist die Zählung
feiertagsblind (nur Wochenende).

Anker: Mittwoch 2026-12-23.  Gesetzliche Feiertage DE im Zeitraum:
Fr 2026-12-25 (Erster Weihnachtstag), Sa 2026-12-26 (Zweiter Weihnachtstag --
ohnehin Wochenende), Fr 2027-01-01 (Neujahr).

DE (überspringt Weihnachten + Neujahr), ab Mi 12-23:
    Do24(1) Mo28(2) Di29(3) Mi30(4) Do31(5) Mo Jan4(6)
Feiertagsblind (nur Wochentage):
    Do24(1) Fr25(2) Mo28(3)
"""
from datetime import date, datetime, timedelta

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

import pytest

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Mittwoch


def start(text, jurisdiction=None):
    r = extract_timespan(text, "de", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} wurde nicht aufgelöst"
    return r[0].start


def nomatch(text, jurisdiction=None):
    r = extract_timespan(text, "de", ANCHOR, jurisdiction=jurisdiction)
    assert r is None, f"{text!r} unerwartet aufgelöst zu {r!r}"


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("in 1 Werktag", date(2026, 12, 24)),
    ("in 2 Werktagen", date(2026, 12, 28)),
    ("in 3 Werktagen", date(2026, 12, 29)),
    ("in 4 Werktagen", date(2026, 12, 30)),
    ("in 5 Werktagen", date(2026, 12, 31)),
    ("in 6 Werktagen", date(2027, 1, 4)),
    ("4 Arbeitstage", date(2026, 12, 30)),
])
def test_zaehlung_de(text, expected):
    assert start(text, "DE") == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("in 1 Werktag", date(2026, 12, 24)),
    ("in 2 Werktagen", date(2026, 12, 25)),   # feiertagsblind
    ("in 3 Werktagen", date(2026, 12, 28)),
])
def test_zaehlung_feiertagsblind(text, expected):
    assert start(text) == _ad(expected)


def test_naechster_werktag():
    assert start("der nächste Werktag", "DE") == _ad(date(2026, 12, 24))


@pytest.mark.parametrize("text,expected,juris", [
    ("3 Werktage nach Weihnachten", date(2026, 12, 30), "DE"),
    ("3 Werktage nach Weihnachten", date(2026, 12, 30), None),
    ("2 Werktage vor Weihnachten", date(2026, 12, 23), "DE"),
])
def test_komposition(text, expected, juris):
    assert start(text, juris) == _ad(expected)


def test_ein_tag_breit():
    r = extract_timespan("in 3 Werktagen", "de", ANCHOR, jurisdiction="DE")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["wie gewohnt", "alles normal"])
def test_negative(text):
    nomatch(text)
    nomatch(text, "DE")
