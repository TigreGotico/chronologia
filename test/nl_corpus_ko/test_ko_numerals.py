"""The two numeral series, and the counter that chooses between them.

Korean writes every number twice over.  The native series counts the hours of
the clock; the Sino-Korean series counts the minutes beside them and every
calendar field.  A numeral therefore has no value of its own here -- it has a
value only in the company of a counter, and the wrong series in a slot names
nothing at all rather than the number it would name elsewhere.
"""
import pytest

from chronologia.extract.numfold_korean import read_native, read_sino

from ._corpus import minute_at, nomatch, start_end


@pytest.mark.parametrize("text,value", [
    ("하나", 1), ("한", 1), ("둘", 2), ("두", 2), ("셋", 3), ("세", 3),
    ("넷", 4), ("네", 4), ("다섯", 5), ("여섯", 6), ("일곱", 7),
    ("여덟", 8), ("아홉", 9), ("열", 10), ("열하나", 11), ("열둘", 12),
    ("열두", 12), ("스물", 20), ("스무", 20), ("스물하나", 21),
    ("서른", 30), ("마흔", 40), ("쉰", 50), ("예순", 60), ("일흔", 70),
    ("여든", 80), ("아흔", 90), ("아흔아홉", 99),
])
def test_native_series_reads(text, value):
    assert read_native(text) == value


@pytest.mark.parametrize("text,value", [
    ("일", 1), ("이", 2), ("삼", 3), ("사", 4), ("오", 5), ("육", 6),
    ("륙", 6), ("칠", 7), ("팔", 8), ("구", 9), ("십", 10), ("십오", 15),
    ("이십", 20), ("이십오", 25), ("삼십", 30), ("사십오", 45),
    ("오십구", 59), ("백", 100), ("천", 1000),
])
def test_sino_series_reads(text, value):
    assert read_sino(text) == value


@pytest.mark.parametrize("text,value", [
    # myriad grouping: every scale word closes the group before it and
    # multiplies it by a power of ten thousand, so 조 is 10^12 and not 10^9.
    ("이만", 20000),
    ("이천이십사", 2024),
    ("삼천오백만", 35000000),
    ("일억", 100000000),
    ("천억", 100000000000),
    ("일조", 1000000000000),
])
def test_sino_groups_by_ten_thousands(text, value):
    assert read_sino(text) == value


@pytest.mark.parametrize("text", ["만", "억", "조"])
def test_a_bare_myriad_scale_carries_no_count(text):
    """만 with no multiplier is the "if" of 만일, not ten thousand of
    anything, so it reads as no number at all."""
    assert read_sino(text) is None


@pytest.mark.parametrize("text", ["하나", "세", "열둘", "스무"])
def test_the_native_series_is_not_read_as_sino(text):
    assert read_sino(text) is None


@pytest.mark.parametrize("text", ["삼", "십오", "이십"])
def test_the_sino_series_is_not_read_as_native(text):
    assert read_native(text) is None


@pytest.mark.parametrize("text,hour", [
    ("한 시", 1), ("두 시", 2), ("세 시", 3), ("네 시", 4), ("다섯 시", 5),
    ("여섯 시", 6), ("일곱 시", 7), ("여덟 시", 8), ("아홉 시", 9),
    ("열 시", 10), ("열한 시", 11), ("열두 시", 12),
])
def test_the_hour_takes_the_native_series(text, hour):
    """Every spelled hour of the twelve, in the attributive shapes."""
    y, m, d = (2027, 5, 12) if hour > 13 else (2027, 5, 13)
    assert start_end(text) == minute_at(y, m, d, hour, 0)


@pytest.mark.parametrize("text", [
    "삼 시", "일 시", "십 시", "십이 시", "오 시",
])
def test_a_sino_numeral_names_no_hour(text):
    """The Sino series counts everything except the hour, so 삼 시 is not
    three o'clock -- it is nothing, and the phrase refuses rather than
    guessing at the number a different counter would have given it."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "세 분", "한 분", "열두 분", "스무 분", "다섯 분",
])
def test_a_native_numeral_names_no_minute(text):
    """The mirror refusal, on the other side of the same rule."""
    nomatch(text)


@pytest.mark.parametrize("text", ["세 초", "두 초", "네 년", "세 일"])
def test_a_native_numeral_counts_no_second_or_calendar_field(text):
    nomatch(text)
