"""Weekday names, and the relative clause that trails one."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, day, nomatch, start_end


#: CLDR wide name, CLDR abbreviation, Monday-first index.
WEEKDAYS = [
    ("Litinin", "Lit", 0),
    ("Talata", "Tal", 1),
    ("Laraba", "Lar", 2),
    ("Alhamis", "Alh", 3),
    ("Jummaʼa", "Jum", 4),
    ("Asabar", "Asa", 5),
    ("Lahadi", "Lah", 6),
]


def _forward(idx):
    """The first date with weekday ``idx`` strictly after the anchor's day."""
    d = ANCHOR.date() + timedelta(days=1)
    while d.weekday() != idx:
        d += timedelta(days=1)
    return (d.year, d.month, d.day)


def _backward(idx):
    """The last date with weekday ``idx`` strictly before the anchor's day."""
    d = ANCHOR.date() - timedelta(days=1)
    while d.weekday() != idx:
        d -= timedelta(days=1)
    return (d.year, d.month, d.day)


@pytest.mark.parametrize("wide,abbr,idx", WEEKDAYS)
def test_a_bare_weekday_is_its_next_occurrence(wide, abbr, idx):
    assert start_end(wide) == day(*_forward(idx))


@pytest.mark.parametrize("wide,abbr,idx", WEEKDAYS)
def test_the_trailing_past_clause_reaches_the_previous_one(wide, abbr, idx):
    assert start_end(f"{wide} da ta gabata") == day(*_backward(idx))


@pytest.mark.parametrize("wide,abbr,idx", WEEKDAYS)
def test_the_masculine_agreement_reads_the_same_way(wide, abbr, idx):
    """ya, ta and suka are one marker: the noun chose which is grammatical."""
    assert start_end(f"{wide} da ya gabata") == day(*_backward(idx))


@pytest.mark.parametrize("wide,abbr,idx", WEEKDAYS)
def test_wuce_is_gabata(wide, abbr, idx):
    """CLDR writes wuce beside gabata for Friday and Saturday; both read."""
    assert start_end(f"{wide} da ta wuce") == day(*_backward(idx))


@pytest.mark.parametrize("wide,abbr,idx", WEEKDAYS)
def test_an_abbreviation_reads_only_beside_a_marker(wide, abbr, idx):
    """Three-letter forms bind a marker-ed order, never a bare weekday."""
    assert start_end(f"{abbr} da ta gabata") == day(*_backward(idx))


def test_a_bare_abbreviation_is_not_a_weekday():
    """Lah, Lar and Lit on their own are ordinary letter runs."""
    for abbr in ("Lah", "Lar", "Lit", "Alh"):
        nomatch(abbr)


def test_friday_reads_in_both_cldr_spellings():
    """ca-gregorian doubles the m, dateFields does not; both are CLDR's."""
    assert start_end("Jummaʼa") == start_end("Jumaʼa")


def test_friday_reads_with_a_plain_apostrophe():
    """The modifier apostrophe U+02BC folds to the ASCII one."""
    assert start_end("Juma'a") == start_end("Jumaʼa")


def test_the_week_starts_on_monday():
    """Nigeria takes CLDR's 001 default, so this week runs Monday to Monday."""
    start, end = start_end("wannan satin")
    assert (start, end) == (ad(ANCHOR.replace(hour=0, minute=0)
                               - timedelta(days=ANCHOR.weekday())),
                            ad(ANCHOR.replace(hour=0, minute=0)
                               + timedelta(days=7 - ANCHOR.weekday())))
