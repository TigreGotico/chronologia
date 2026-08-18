"""Lithuanian relative offsets in both directions.

"prieš" + accusative shifts back ("prieš tris dienas" = three days ago) and
"po" + genitive shifts forward ("po trijų dienų" = in three days).  Both are
prefix markers; Lithuanian does not postpose them.  The counted noun's form
comes from the numeral, so each direction is exercised across the three
government classes.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, parse, span, start


@pytest.mark.parametrize("n,form", [(1, "dieną"), (2, "dienas"), (3, "dienas"),
                                    (9, "dienas"), (11, "dienų"),
                                    (20, "dienų"), (21, "dieną")])
def test_days_past(n, form):
    assert start(f"prieš {n} {form}") == ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "dienos"), (3, "dienų"), (11, "dienų"),
                                    (30, "dienų")])
def test_days_future(n, form):
    assert start(f"po {n} {form}") == ad(ANCHOR + timedelta(days=n))


@pytest.mark.parametrize("n,form", [(1, "savaitę"), (2, "savaites"),
                                    (5, "savaites"), (11, "savaičių")])
def test_weeks_past(n, form):
    assert start(f"prieš {n} {form}") == ad(ANCHOR - timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(2, "savaičių"), (5, "savaičių")])
def test_weeks_future(n, form):
    assert start(f"po {n} {form}") == ad(ANCHOR + timedelta(weeks=n))


@pytest.mark.parametrize("n,form", [(1, "mėnesį"), (2, "mėnesius"),
                                    (11, "mėnesių")])
def test_months_past(n, form):
    assert start(f"prieš {n} {form}") == ad(ANCHOR - relativedelta(months=n))


@pytest.mark.parametrize("n,form", [(2, "mėnesių"), (6, "mėnesių")])
def test_months_future(n, form):
    assert start(f"po {n} {form}") == ad(ANCHOR + relativedelta(months=n))


@pytest.mark.parametrize("n", [1, 2, 5, 10, 100])
def test_years_past(n):
    assert start(f"prieš {n} metus") == ad(ANCHOR - relativedelta(years=n))


@pytest.mark.parametrize("n", [1, 5, 100])
def test_years_future(n):
    assert start(f"po {n} metų") == ad(ANCHOR + relativedelta(years=n))


@pytest.mark.parametrize("n,form", [(5, "minutes"), (30, "minučių"),
                                    (45, "minučių")])
def test_minutes_past(n, form):
    assert start(f"prieš {n} {form}") == ad(ANCHOR - timedelta(minutes=n))


@pytest.mark.parametrize("n,form", [(2, "valandas"), (10, "valandų")])
def test_hours_past(n, form):
    assert start(f"prieš {n} {form}") == ad(ANCHOR - timedelta(hours=n))


@pytest.mark.parametrize("phrase,delta", [
    ("prieš penkias dienas", timedelta(days=-5)),
    ("prieš tris savaites", timedelta(weeks=-3)),
    ("prieš dešimt minučių", timedelta(minutes=-10)),
    ("po trijų dienų", timedelta(days=3)),
    ("po dviejų savaičių", timedelta(weeks=2)),
    ("po dvidešimt penkių dienų", timedelta(days=25)),
])
def test_spelled_offset(phrase, delta):
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("phrase,delta", [
    ("prieš dieną", timedelta(days=-1)),
    ("prieš savaitę", timedelta(weeks=-1)),
    ("prieš valandą", timedelta(hours=-1)),
    ("prieš minutę", timedelta(minutes=-1)),
    ("po dienos", timedelta(days=1)),
    ("po savaitės", timedelta(weeks=1)),
    ("po valandos", timedelta(hours=1)),
])
def test_bare_singular_offset(phrase, delta):
    """A count of one is left unsaid; the marker plus the singular noun is the
    whole offset."""
    assert start(phrase) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("susitinkame po trijų dienų", timedelta(days=3)),
    ("priminki man po dviejų mėnesių", relativedelta(months=2)),
    ("tai buvo prieš tris dienas", timedelta(days=-3)),
])
def test_sentence_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("word,off", [("šiandien", 0), ("rytoj", 1),
                                      ("vakar", -1), ("poryt", 2),
                                      ("užvakar", -2)])
def test_named_day(word, off):
    assert start(word) == ad((ANCHOR + timedelta(days=off)).replace(
        hour=0, minute=0))


_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("kitą pirmadienį", _MID + timedelta(days=6)),
    ("kitą penktadienį", _MID + timedelta(days=3)),
    ("praeitą penktadienį", _MID - timedelta(days=4)),
    ("praeitą antradienį", _MID - timedelta(days=7)),
    ("praeitą trečiadienį", _MID - timedelta(days=6)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text", ["kitą penktadienį", "praeitą trečiadienį"])
def test_weekday_marker_consumed(text):
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,expected_start,expected_days", [
    ("šią savaitę", _MID - timedelta(days=1), 7),
    ("praeitą savaitę", _MID - timedelta(days=8), 7),
    ("kitą savaitę", _MID + timedelta(days=6), 7),
    ("šį mėnesį", _MID.replace(day=1), 30),
])
def test_accusative_period(text, expected_start, expected_days):
    s = span(text)
    assert s.start == ad(expected_start)
    assert (s.end - s.start).days == expected_days


def test_offset_needs_marker():
    nomatch("penkias dienas")
    nomatch("trys dienos")
    assert parse("3 po") is None or parse("3 po")[0].start.date() == ANCHOR.date()
