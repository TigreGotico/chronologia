"""French "huit jours" and "quinze jours": one week and two weeks.

French counts these days inclusively, the first day and the last:

* Académie française, 9th edition, s.v. "huit": "Huit jours, dans l'usage
  courant, une semaine entière en comptant le premier jour et le dernier.
  J'irai vous voir dans huit jours, avant huit jours, sous huit jours."
* Académie française, 9th edition, s.v. "quinze": "Quinze jours, dans l'usage
  courant, deux semaines complètes."
* TLFi (CNRTL) s.v. "huit", I.A: "P. ext. Huit jours. Une semaine."; s.v.
  "quinze": "P. ext. Quinze jours. Deux semaines. Tous les quinze jours".
* Larousse s.v. "huit": "Huit jours, une semaine."

So "dans huit jours" is seven days after the anchor, as "dans 7 jours" is,
and "dans quinze jours" fourteen.  Portuguese reads "quinze dias" as fifteen
days (ruling 18) because its dictionaries give no such sense; the French ones
do.  Business days are counted as written: "dans 8 jours ouvrés" is eight
working days.

Expected values are hand-computed from the calendar of November and December
2026, never read back from the parser.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_recurrence

from ._corpus import ad, nomatch, parse

A = datetime(2026, 11, 26, 10, 0)   # a Thursday


@pytest.mark.parametrize("text,start", [
    ("dans huit jours", datetime(2026, 12, 3, 10, 0)),
    ("dans quinze jours", datetime(2026, 12, 10, 10, 0)),
    # the digits are counted as written: the sense is that of the spoken
    # numeral, and a written count of days is literal in law (Code de
    # procédure civile, art. 641-642)
    ("dans 8 jours", datetime(2026, 12, 4, 10, 0)),
    ("dans 15 jours", datetime(2026, 12, 11, 10, 0)),
    # a count beside a larger unit is part of a literal sum
    ("dans 2 mois et quinze jours", datetime(2027, 2, 10, 10, 0)),
    ("il y a un an et quinze jours", datetime(2025, 11, 11, 10, 0)),
    ("il y a huit jours", datetime(2026, 11, 19, 10, 0)),
    ("il y a quinze jours", datetime(2026, 11, 12, 10, 0)),
    # other counts are read as written
    ("dans neuf jours", datetime(2026, 12, 5, 10, 0)),
    ("dans dix-huit jours", datetime(2026, 12, 14, 10, 0)),
    ("dans 16 jours", datetime(2026, 12, 12, 10, 0)),
])
def test_huit_and_quinze_jours_are_one_and_two_weeks(text, start):
    r = parse(text, A)
    assert r is not None, f"{text!r} did not parse"
    assert (r[0].start, r[0].end) == (ad(start), ad(start + timedelta(days=1)))
    assert r.remainder == ""


@pytest.mark.parametrize("text,day", [
    # an ordinal day is not the count: the fifteenth and the eighth day
    ("le quinzième jour de mars", datetime(2027, 3, 15)),
    ("le 15e jour de mars", datetime(2027, 3, 15)),
    ("le huitième jour de mars", datetime(2027, 3, 8)),
])
def test_ordinal_day_is_not_the_count(text, day):
    r = parse(text, A)
    assert r is not None
    assert r[0].start == ad(day)


@pytest.mark.parametrize("text", [
    "dans quinze jours calendaires",
    "dans quinze jours francs",
    "dans quinze jours pleins",
    "dans quinze jours entiers",
    "dans quinze jours de travail",
])
def test_a_counted_kind_of_day_is_literal(text):
    # "jours francs", "calendaires", "pleins", "entiers", "de travail" count
    # each day: the count stays fifteen, whatever else reads
    r = parse(text, A)
    assert r is None or r[0].start != ad(datetime(2026, 12, 10, 10, 0))


def test_a_delai_is_literal():
    from chronologia import extract_duration
    got = extract_duration("un délai de quinze jours", "fr", anchor=A)
    assert got is None or got.duration == timedelta(days=15)


def test_dans_huit_jours_with_another_weekday_refuses():
    # A count of days reaches one day, and a weekday beside it must be that
    # day's (ruling 19, as "dans 7 jours vendredi" refuses).  Seven days on is
    # Thursday 3 December, not a Friday, so the phrase names no day.
    nomatch("dans huit jours vendredi", A)
    r = parse("dans huit jours jeudi", A)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 12, 3))


def test_business_days_are_counted_as_written():
    # Fri 27 Nov, Mon 30, Tue 1, Wed 2, Thu 3, Fri 4, Mon 7, Tue 8 Dec
    r = parse("dans 8 jours ouvrés", A)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 12, 8))


@pytest.mark.parametrize("text,days", [
    ("pendant huit jours", 7),
    ("pendant quinze jours", 14),
    ("pendant neuf jours", 9),
])
def test_length(text, days):
    got = extract_duration(text, "fr", anchor=A)
    assert got is not None
    assert got.duration == timedelta(days=days)


def test_tous_les_quinze_jours_is_every_two_weeks():
    got = extract_recurrence("tous les quinze jours", "fr", A)
    assert got is not None
    assert got.recurrence.to_string() == "FREQ=DAILY;INTERVAL=14"


def test_tous_les_15_jours_is_counted_as_written():
    got = extract_recurrence("tous les 15 jours", "fr", A)
    assert got is not None
    assert got.recurrence.to_string() == "FREQ=DAILY;INTERVAL=15"
