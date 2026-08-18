"""Serbian calendar dates (digit day and spelled genitive-masculine ordinal
day) and offsets in both directions, both scripts.

"pre" doubles as "before X" and "ago" ("pre tri dana" = three days ago),
+genitive -- Wiktionary, pre; Talkpal, "Telling Time in Serbian".  Compound
day-ordinals (21st, 25th, 31st) leave the tens a bare cardinal and decline
only the unit ("dvadeset petog" = 25th), mirroring hr's tens-prefix
composition.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_slavic import sr_lat2cyr

from ._corpus import ANCHOR, ad, nomatch, remainder, span, start


def _cyr(phrase: str) -> str:
    return " ".join(sr_lat2cyr(w) for w in phrase.split())


# -- calendar dates: digit day -----------------------------------------------

@pytest.mark.parametrize("phrase,y,m,d", [
    ("5. maj 2020.", 2020, 5, 5),
    ("25. decembar 2019.", 2019, 12, 25),
    ("1. januar", 2018, 1, 1),
])
def test_digit_day_dates(phrase, y, m, d):
    r = start(phrase)
    assert (r.year, r.month, r.day) == (y, m, d)


# -- calendar dates: spelled genitive-masculine ordinal day -----------------

@pytest.mark.parametrize("phrase,m,d", [
    ("petog maja", 5, 5),
    ("prvog januara", 1, 1),
    ("desetog oktobra", 10, 10),
    ("dvadeset petog decembra", 12, 25),
    ("tridesetog aprila", 4, 30),
])
def test_spelled_ordinal_day_dates(phrase, m, d):
    r = start(phrase)
    assert (r.month, r.day) == (m, d)


@pytest.mark.parametrize("phrase,m,d", [
    ("петог маја", 5, 5),
    ("двадесет петог децембра", 12, 25),
])
def test_spelled_ordinal_day_dates_cyrillic(phrase, m, d):
    r = start(phrase)
    assert (r.month, r.day) == (m, d)


# -- offsets: "pre" as ago AND before, +genitive -----------------------------

@pytest.mark.parametrize("n,unit,delta", [
    (3, "dana", timedelta(days=3)),
    (2, "sata", timedelta(hours=2)),
    (5, "minuta", timedelta(minutes=5)),
])
def test_pre_as_ago(n, unit, delta):
    assert start(f"pre {n} {unit}") == ad(ANCHOR - delta)


@pytest.mark.parametrize("n,unit,delta", [
    (3, "dana", timedelta(days=3)),
    (2, "sata", timedelta(hours=2)),
])
def test_pre_as_ago_cyrillic(n, unit, delta):
    phrase = f"{sr_lat2cyr('pre')} {n} {sr_lat2cyr(unit)}"
    assert start(phrase) == ad(ANCHOR - delta)


@pytest.mark.parametrize("n,unit,delta", [
    (3, "dana", timedelta(days=3)),
    (2, "sata", timedelta(hours=2)),
    (5, "minuta", timedelta(minutes=5)),
])
def test_za_as_from_now(n, unit, delta):
    assert start(f"za {n} {unit}") == ad(ANCHOR + delta)


def test_offset_directions_are_not_symmetric():
    """Adversarial: "pre" and "za" must resolve to opposite sides of the
    anchor for the identical count/unit."""
    ago = start("pre pet dana")
    hence = start("za pet dana")
    assert ago < ad(ANCHOR) < hence


# -- weekday / weekend / named days, both scripts ----------------------------

@pytest.mark.parametrize("phrase,offset", [
    ("danas", 0), ("sutra", 1), ("juče", -1),
    ("prekjuče", -2), ("prekosutra", 2),
])
def test_named_days_latin(phrase, offset):
    got = span(phrase).start
    want = ad(ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
              + timedelta(days=offset))
    assert got == want


@pytest.mark.parametrize("phrase,offset", [
    ("данас", 0), ("сутра", 1), ("јуче", -1),
    ("прекјуче", -2), ("прекосутра", 2),
])
def test_named_days_cyrillic(phrase, offset):
    got = span(phrase).start
    want = ad(ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
              + timedelta(days=offset))
    assert got == want


@pytest.mark.parametrize("phrase", ["vikend", "викенд"])
def test_weekend(phrase):
    r = start(phrase)
    assert r.date().weekday() == 5  # Saturday


@pytest.mark.parametrize("phrase", ["sledeći ponedeljak", "prošli petak",
                                    "следећи понедељак", "прошли петак"])
def test_next_last_weekday(phrase):
    r = span(phrase)
    assert (r.end - r.start) == timedelta(days=1)


@pytest.mark.parametrize("phrase,year_offset", [
    ("sledeće godine", 1), ("prošle godine", -1), ("ove godine", 0),
    ("следеће године", 1), ("прошле године", -1), ("ове године", 0),
])
def test_this_next_last_year(phrase, year_offset):
    r = span(phrase)
    assert r.start.year == ANCHOR.year + year_offset
    assert r.start.month == 1 and r.start.day == 1


def test_between_construction():
    """"između X i Y" -- Wiktionary, između; the "i" glue is the ordinary
    conjunction (marker_and.voc)."""
    r = span("između januara i marta")
    assert r.start.month == 1
