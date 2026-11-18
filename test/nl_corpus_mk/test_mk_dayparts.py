"""The five day-part bands, asserted at the exact hours CLDR draws them.

Macedonian splits the forenoon: наутро runs from four to ten and претпладне
holds the two hours before noon on its own, the same shape German draws with
Morgen and Vormittag.  The afternoon runs to six and the evening from there to
midnight, leaving the small hours to ноќе.  Noon and midnight are points, not
bands, and are read as clock landmarks.

Every boundary below is a half-open interval: the opening hour belongs to the
band and the closing hour belongs to the next one.
"""
import pytest

from ._corpus import ad, parse, span, start_end
from datetime import datetime

# A band that has ended at the 13:04 anchor is tomorrow's (ruling 28).
BANDS = [
    ("ноќе", 0, 4, 13),
    ("наутро", 4, 10, 13),
    ("претпладне", 10, 12, 13),
    ("попладне", 12, 18, 12),
    ("навечер", 18, 24, 12),
]


def _band(hour_from, hour_to, day):
    base = datetime(2027, 5, day)
    return (ad(base.replace(hour=hour_from)),
            ad(base.replace(hour=hour_to % 24) if hour_to < 24
               else datetime(2027, 5, day + 1)))


@pytest.mark.parametrize("text,hour_from,hour_to,day", BANDS)
def test_each_band_runs_between_its_cldr_hours(text, hour_from, hour_to, day):
    assert start_end(text) == _band(hour_from, hour_to, day)


@pytest.mark.parametrize("text,hour_from,hour_to,day", BANDS)
def test_a_band_opens_on_its_own_first_hour(text, hour_from, hour_to, day):
    s = span(text)
    assert s.start.hour == hour_from


@pytest.mark.parametrize("text,hour_from,hour_to,day", BANDS)
def test_a_band_closes_before_the_next_ones_first_hour(text, hour_from,
                                                       hour_to, day):
    s = span(text)
    assert (s.end.hour or 24) == hour_to


def test_the_forenoon_is_not_swallowed_by_the_morning():
    # претпладне is two hours, not the whole 04:00-12:00 stretch наутро opens.
    morning = span("наутро")
    forenoon = span("претпладне")
    assert morning.end.hour == 10 and forenoon.start.hour == 10
    assert forenoon.end.hour == 12


@pytest.mark.parametrize("text,hour_from", [
    ("утро", 4), ("вечер", 18),
])
def test_the_stand_alone_spellings_name_the_same_bands(text, hour_from):
    assert span(text).start.hour == hour_from


@pytest.mark.parametrize("text,date_", [
    ("вчера навечер", (2027, 5, 11)),
    ("утре наутро", (2027, 5, 13)),
    ("денес попладне", (2027, 5, 12)),
])
def test_a_named_day_narrows_to_a_band(text, date_):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == date_


def test_noon_and_midnight_are_points_not_bands():
    for text in ("пладне", "полноќ"):
        s = span(text)
        assert (s.end - s.start).total_seconds() == 60
