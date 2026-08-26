"""What this locale declines to read, and why declining is the right answer.

Every case here is a phrase whose competing readings are both ordinary
Korean and which carries nothing to choose between them.  Returning one of
them would hand a caller a confident wrong answer with no sign that anything
was guessed, so the phrase resolves to nothing instead.
"""
import pytest

from chronologia.extract.numfold_korean import split_word

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", ["삼 시", "십 시", "일 시", "십이 시"])
def test_a_sino_numeral_in_the_hour_slot_refuses(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["세 분", "열두 분", "두 초"])
def test_a_native_numeral_in_the_minute_slot_refuses(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["일", "월"])
def test_the_two_worst_homographs_name_nothing_on_their_own(text):
    """일 is the day, the numeral one and Sunday; 월 is the month and
    Monday.  Neither is decided by anything inside the word."""
    nomatch(text)


@pytest.mark.parametrize("text", ["만일", "일일"])
def test_an_ordinary_word_is_not_segmented_into_a_count(text):
    """만일 is "if" and 일일 is "daily".  Both would segment cleanly into a
    Sino numeral plus the day counter, so both are carved out by hand rather
    than read as ten thousand days and one day."""
    assert split_word(text) is None
    nomatch(text)


@pytest.mark.parametrize("text", ["시일", "일요일", "오후", "이번"])
def test_a_word_merely_containing_a_counter_is_left_whole(text):
    """The segmenter licenses a counter only behind a numeral of the series
    that counter selects, and requires the segmentation to cover the word
    exactly, so an ordinary word that happens to contain 시 or 일 is not cut
    apart into a time."""
    assert split_word(text) is None


@pytest.mark.parametrize("text", ["시", "분", "초", "년", "개월", "주"])
def test_a_bare_counter_with_no_count_is_not_an_offset(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["13월", "0월", "99월"])
def test_a_month_number_the_calendar_has_no_month_for_refuses(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["유월", "시월"])
def test_the_unsourced_spelled_month_names_refuse(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["하나", "열둘", "이십오", "삼천"])
def test_a_bare_numeral_is_not_a_date(text):
    """A count with nothing counted names no time -- and in Korean it does
    not even name a number, because no counter has told it which series it
    belongs to."""
    nomatch(text)


@pytest.mark.parametrize("text,parts", [
    ("지난주에", ("지난", "주")),
    ("열두시반에", ("열두", "시", "반")),
])
def test_a_particle_comes_off_before_the_compound_is_read(text, parts):
    """The particle is written onto the noun with no space, so it has to be
    cut off first -- otherwise the noun underneath it never reaches the
    segmenter and the whole phrase is lost."""
    assert parse(text) is not None
    assert split_word(text) is None
    assert split_word(text[:-1]) == parts
