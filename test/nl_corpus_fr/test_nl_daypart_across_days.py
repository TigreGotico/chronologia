"""French "la nuit de samedi à dimanche": a part of the day named by a range
of days refuses.

"la nuit de samedi à dimanche" is the night that runs from Saturday into
Sunday.  TLFi (CNRTL) s.v. "nuit", II.A, gives the night as the time "depuis
la disparition de la lumière qui suit le coucher du soleil jusqu'à
l'apparition du jour qui precède le lever du soleil", which depends on the
place and the season, and a fixed clock band only in law ("DR. Espace de temps
qui s'étend de 21 heures à 6 heures").  The locale's "nuit" band is the small
hours of one day (Unicode CLDR 47, fr), so it cannot hold a night that starts
the evening before.  "le soir du 3 au 5 mai" names three evenings, no single
span.  So these phrases return nothing.

Before this fix "dans la nuit de samedi à dimanche" said on Thursday
26 November 2026 read 00:00 to 04:00 of that Thursday: a wrong span.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, parse

THU = datetime(2026, 11, 26, 10, 0)   # a Thursday


@pytest.mark.parametrize("text", [
    "dans la nuit de samedi à dimanche",
    "la nuit de samedi à dimanche",
    "la nuit du samedi au dimanche",
    "nuit de samedi à dimanche",
    "les nuits de samedi à dimanche",
    "la nuit du 28 au 29 novembre",
    "dans la nuit du 28 au 29",
    "la nuit d'hier à aujourd'hui",
    "le soir du 3 au 5 mai",
    "la soirée du 3 au 5 mai",
    "la matinée du 3 au 5 mai",
    "l'après-midi du lundi au vendredi",
    "les après-midis du 3 au 5 mai",
    "la nuitée du 28 au 29 novembre",
    "le soir du lundi au vendredi",
])
def test_daypart_over_a_range_of_days_refuses(text):
    nomatch(text, THU)


@pytest.mark.parametrize("text,start,end", [
    # one day named: the locale's own band of that day still reads
    ("la nuit de samedi", datetime(2026, 11, 28, 0, 0),
     datetime(2026, 11, 28, 4, 0)),
    ("samedi soir", datetime(2026, 11, 28, 18, 0),
     datetime(2026, 11, 29, 0, 0)),
    # a range of days with no part of the day is unchanged
    ("de samedi à dimanche", datetime(2026, 11, 28, 0, 0),
     datetime(2026, 11, 30, 0, 0)),
])
def test_one_day_or_no_daypart_still_reads(text, start, end):
    r = parse(text, THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(start), ad(end))
    assert r.remainder == ""


@pytest.mark.parametrize("text", [
    # a number after "à" with a weekday before it is a clock: 21:00 on
    # Saturday 28 November, as "le soir" fixes the half of the day
    "le soir de samedi à 9",
    "le soir de samedi à neuf",
])
def test_a_clock_after_a_to_word_is_not_a_range_of_days(text):
    r = parse(text, THU)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 11, 28, 21, 0))


def test_an_address_after_au_is_not_a_range_of_days():
    r = parse("le soir de samedi au 12 rue Victor Hugo", THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(datetime(2026, 11, 28, 18, 0)),
                                      ad(datetime(2026, 11, 29, 0, 0)))


def test_event_keeps_the_clock():
    from chronologia import extract_event
    got = extract_event("réunion le soir de samedi à 9", "fr", THU)
    assert got is not None
    assert got.span.start == ad(datetime(2026, 11, 28, 21, 0))


def test_every_view_refuses_the_range_of_evenings():
    from chronologia import extract_candidates, extract_event
    assert extract_candidates("le soir du lundi au vendredi", "fr", THU) == []
    assert extract_event("réunion le soir du lundi au vendredi", "fr",
                         THU) is None


def test_a_dated_evening_keeps_its_clock():
    # "à 9" after a whole date is a clock: 21:00 on 28 November 2026
    r = parse("le soir du 28 novembre à 9", THU)
    assert r is not None
    assert r[0].start == ad(datetime(2026, 11, 28, 21, 0))


@pytest.mark.parametrize("text", [
    "le soir. De samedi à dimanche",
    "le soir de samedi, la réunion est reportée à lundi",
])
def test_no_range_of_days_across_a_break(text):
    # the part of the day does not govern a range in another clause or
    # sentence, so the phrase is not refused outright
    assert parse(text, THU) is not None
