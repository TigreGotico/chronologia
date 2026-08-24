"""The four Armenian day-part bands and the suffixed definite article.

CLDR gives ``hy`` the same carve-up it gives Icelandic and Lithuanian: the
morning opens at 06:00, the evening runs to midnight and the night is the
small hours.  Each band has a stand-alone name and a format name, and the
consonant-final nouns also appear with the suffixed definite article, so all
three surfaces must reach the same band.
"""
import pytest

from ._corpus import ANCHOR, span, start


def _band(text):
    s = span(text)
    return (s.start.hour, s.start.minute), (s.end.hour, s.end.minute)


@pytest.mark.parametrize("text", ["առավոտ", "առավոտյան", "առավոտը"])
def test_morning_opens_at_six(text):
    assert _band(text) == ((6, 0), (12, 0))


@pytest.mark.parametrize("text", ["ցերեկ", "ցերեկը", "ցերեկվա"])
def test_afternoon(text):
    assert _band(text) == ((12, 0), (18, 0))


@pytest.mark.parametrize("text", ["երեկո", "երեկոյան", "երեկոն"])
def test_evening_runs_to_midnight(text):
    assert _band(text) == ((18, 0), (0, 0))


@pytest.mark.parametrize("text", ["գիշեր", "գիշերը", "գիշերվա"])
def test_night_is_the_small_hours(text):
    assert _band(text) == ((0, 0), (6, 0))


def test_evening_and_night_do_not_overlap():
    """The evening closing at midnight and the night opening there is the
    whole point of this locale's band shape; an overlap would make an evening
    time resolvable two ways."""
    assert _band("երեկո")[1] == (0, 0) == _band("գիշեր")[0]


@pytest.mark.parametrize("text,hour", [
    ("կեսօր", 12), ("կեսօրին", 12), ("կեսգիշեր", 0), ("կեսգիշերին", 0),
])
def test_noon_and_midnight_are_instants(text, hour):
    s = span(text)
    assert s.start.hour == hour
    assert (s.end - s.start).total_seconds() == 60
