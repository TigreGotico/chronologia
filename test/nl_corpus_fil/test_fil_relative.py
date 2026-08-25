"""Offsets, named days and day-parts.

Filipino marks temporal direction with a preposition rather than with
anything on the time noun: ``sa`` leads a future reference and ``noong`` a
past one, and the noun itself is invariant between the two.  Both marker
positions are exercised, and each direction is pinned against the other.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, span, start, start_end


@pytest.mark.parametrize("text,delta", [
    ("sa isang araw", timedelta(days=1)),
    ("sa dalawang araw", timedelta(days=2)),
    ("sa tatlong araw", timedelta(days=3)),
    ("sa sampung araw", timedelta(days=10)),
    ("sa dalawang oras", timedelta(hours=2)),
    ("sa tatlumpung minuto", timedelta(minutes=30)),
    ("sa dalawang semana", timedelta(weeks=2)),
])
def test_sa_leads_a_future_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("noong dalawang araw", timedelta(days=2)),
    ("noong tatlong araw", timedelta(days=3)),
    ("noong dalawang semana", timedelta(weeks=2)),
])
def test_noong_leads_a_past_offset(text, delta):
    assert start(text) <= ad(ANCHOR - delta) + timedelta(0)
    assert start(text).day == (ANCHOR - delta).day


@pytest.mark.parametrize("text,delta", [
    ("dalawang araw noon", timedelta(days=2)),
    ("tatlong araw noon", timedelta(days=3)),
    ("dalawang semana noon", timedelta(weeks=2)),
])
def test_the_past_marker_also_trails(text, delta):
    assert start(text).day == (ANCHOR - delta).day


@pytest.mark.parametrize("future,past", [
    ("sa dalawang araw", "noong dalawang araw"),
    ("sa tatlong araw", "dalawang araw noon"),
    ("sa dalawang semana", "dalawang semana noon"),
])
def test_the_two_directions_never_coincide(future, past):
    assert start(future) > ad(ANCHOR)
    assert start(past) < ad(ANCHOR)


@pytest.mark.parametrize("text,day", [
    ("ngayon", 27), ("bukas", 28), ("kahapon", 26), ("kamakalawa", 25),
])
def test_named_days(text, day):
    assert start(text).day == day


WEEKDAYS = ["lunes", "martes", "miyerkules", "huwebes", "biyernes",
            "sabado", "linggo"]


@pytest.mark.parametrize("name,weekday", list(zip(WEEKDAYS, range(7))))
def test_a_bare_weekday_names_the_coming_one(name, weekday):
    s = start(name)
    assert s.datetime().weekday() == weekday
    assert s.datetime() > ANCHOR


@pytest.mark.parametrize("name,weekday", list(zip(WEEKDAYS, range(7))))
def test_noong_selects_the_preceding_weekday(name, weekday):
    s = start(f"noong {name}")
    assert s.datetime().weekday() == weekday
    assert s.datetime() < ANCHOR


@pytest.mark.parametrize("name", WEEKDAYS)
def test_the_past_and_future_weekday_are_a_week_apart(name):
    """A whole number of weeks apart: seven days for any weekday but the
    anchor's own, fourteen for that one, since neither reading may land on
    the anchor day itself."""
    gap = start(name).datetime() - start(f"noong {name}").datetime()
    assert gap in (timedelta(days=7), timedelta(days=14))


@pytest.mark.parametrize("text,band", [
    ("umaga", (0, 12)), ("hapon", (12, 16)), ("gabi", (18, 24)),
])
def test_dayparts_follow_the_cldr_bands(text, band):
    s, e = start_end(text)
    assert s.hour == band[0]
    assert (e.hour or 24) == band[1]


@pytest.mark.parametrize("text,day,hour", [
    ("bukas umaga", 28, 0),
    ("kahapon ng gabi", 26, 18),
])
def test_a_daypart_composes_with_a_named_day(text, day, hour):
    s = start(text)
    assert (s.day, s.hour) == (day, hour)


@pytest.mark.parametrize("text,y", [("taong 2026", 2026), ("2026", 2026)])
def test_year_reference(text, y):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, 1, 1)


def test_a_range_runs_from_mula_to_hanggang():
    s, e = start_end("mula Lunes hanggang Biyernes")
    assert s.datetime().weekday() == 0
    assert e.datetime().weekday() == 5


@pytest.mark.parametrize("text", ["sa", "noong", "hanggang", "mula", "tuwing"])
def test_a_bare_marker_names_nothing(text):
    nomatch(text)
