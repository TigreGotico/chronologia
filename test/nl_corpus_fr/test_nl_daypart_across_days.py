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
    # "à 9" after a whole date is a clock: 21:00 on 28 November 2026, a
    # minute wide
    r = parse("le soir du 28 novembre à 9", THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(datetime(2026, 11, 28, 21, 0)),
                                      ad(datetime(2026, 11, 28, 21, 1)))
    assert r.remainder == ""


def test_a_month_after_a_comma_still_refuses():
    # With "décembre" in the next clause the text names two months, and
    # without this refusal the reader answers this evening (26 November,
    # 18:00) with "du 28 novembre à 9" left over: a wrong span.  No span is
    # the better answer.
    nomatch("le soir du 28 novembre à 9, décembre sera bientôt là", THU)


def test_no_range_of_days_across_a_sentence_break():
    # "le soir" is this evening, 26 November from 18:00 to midnight; the next
    # sentence is not a range it governs
    r = parse("le soir. De samedi à dimanche", THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(datetime(2026, 11, 26, 18, 0)),
                                      ad(datetime(2026, 11, 27, 0, 0)))
    assert r.remainder == "De samedi à dimanche"


def test_the_refusal_does_not_reach_across_a_comma():
    from chronologia.extract.pipeline import pretokens
    from chronologia.extract.reading import _daypart_across_days
    from chronologia.extract.timespan import _timespan_engine
    spec = _timespan_engine("fr").spec
    text = "le soir de samedi, la réunion est reportée à lundi"
    assert not _daypart_across_days(pretokens(text, spec), spec)
    assert _daypart_across_days(
        pretokens("le soir de samedi à lundi", spec), spec)


@pytest.mark.xfail(strict=True, reason=(
    "two weekdays in the text: the day part does not compose with the "
    "first one and reads this evening, as on dev"))
def test_evening_of_saturday_before_a_comma():
    # the evening of Saturday 28 November, from 18:00 to midnight
    r = parse("le soir de samedi, la réunion est reportée à lundi", THU)
    assert r is not None
    assert (r[0].start, r[0].end) == (ad(datetime(2026, 11, 28, 18, 0)),
                                      ad(datetime(2026, 11, 29, 0, 0)))
