"""The five day-part bands, and the two words that are also am/pm markers."""
import pytest

from ._corpus import band, start_end

TODAY = (2027, 5, 12)


@pytest.mark.parametrize("text,expected", [
    ("아침", band(*TODAY, (3, 0), (6, 0))),
    ("오전", band(*TODAY, (6, 0), (12, 0))),
    ("오후", band(*TODAY, (12, 0), (18, 0))),
    ("저녁", band(*TODAY, (18, 0), (21, 0))),
    ("밤", band(*TODAY, (21, 0), (3, 0), days=1)),
])
def test_the_bands(text, expected):
    """Korean cuts the forenoon in two: 아침 is the three hours before the
    working day and 오전 the six after them, so the two are separate bands
    rather than one long morning."""
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("내일 아침", band(2027, 5, 13, (3, 0), (6, 0))),
    ("내일 저녁", band(2027, 5, 13, (18, 0), (21, 0))),
    ("어제 밤", band(2027, 5, 11, (21, 0), (3, 0), days=1)),
])
def test_a_band_on_a_named_day(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,hour", [("오전 9시", 9), ("오후 9시", 21)])
def test_the_band_words_double_as_the_half_day_markers(text, hour):
    """오전 and 오후 name a band in a bare adverbial and mark the half-day in
    a clock phrase; the same two words do both jobs and the slot decides."""
    s, _ = start_end(text)
    assert s.hour == hour


def test_the_two_half_day_readings_of_the_same_hour_differ_by_twelve():
    am, _ = start_end("오전 9시")
    pm, _ = start_end("오후 9시")
    assert pm.hour - am.hour == 12
