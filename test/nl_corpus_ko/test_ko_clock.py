"""The clock: forward from the named hour, backward only when 전 says so."""
import pytest

from ._corpus import minute_at, nomatch, remainder, start_end

#: the anchor's own day and the day after it -- prefer_future rolls a wall
#: time already past on the anchor day forward to the next one.
TODAY = (2027, 5, 12)
TOMORROW = (2027, 5, 13)


@pytest.mark.parametrize("text,expected", [
    ("09:30", minute_at(*TOMORROW, 9, 30)),
    ("15:45", minute_at(*TODAY, 15, 45)),
    ("00:00", minute_at(*TOMORROW, 0, 0)),
    ("21:50", minute_at(*TODAY, 21, 50)),
])
def test_a_digit_clock_reads_verbatim(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("3시 20분", minute_at(*TOMORROW, 3, 20)),
    ("9시 30분", minute_at(*TOMORROW, 9, 30)),
    ("14시 5분", minute_at(*TODAY, 14, 5)),
    ("세 시 십 분", minute_at(*TOMORROW, 3, 10)),
    ("열두 시 이십오 분", minute_at(*TOMORROW, 12, 25)),
    ("네 시 삼십일 분", minute_at(*TOMORROW, 4, 31)),
    ("아홉 시 이십팔 분", minute_at(*TOMORROW, 9, 28)),
])
def test_minutes_are_added_to_the_hour_just_named(text, expected):
    """The counting runs forward: 세 시 십 분 is ten past three, never ten
    to it.  A reversed clock is wrong in every reading it produces and says
    nothing about being wrong, so both directions are pinned."""
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("두 시 반", minute_at(*TOMORROW, 2, 30)),
    ("9시 반", minute_at(*TOMORROW, 9, 30)),
    ("열두시반", minute_at(*TOMORROW, 12, 30)),
    ("세시반", minute_at(*TOMORROW, 3, 30)),
])
def test_half_is_half_past_the_hour_named(text, expected):
    """반 stands in for 삼십 분 and counts forward like any other minute
    count, so 두 시 반 is 2:30 and not 1:30."""
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("세 시 십 분 전", minute_at(*TOMORROW, 2, 50)),
    ("다섯 시 오 분 전", minute_at(*TOMORROW, 4, 55)),
    ("9시 15분 전", minute_at(*TOMORROW, 8, 45)),
    ("열두 시 이십 분 전", minute_at(*TOMORROW, 11, 40)),
])
def test_a_final_jeon_turns_the_count_backward(text, expected):
    """The backward reading exists and is marked, obligatorily and last, by
    전: 세 시 십 분 전 is ten minutes BEFORE three."""
    assert start_end(text) == expected


@pytest.mark.parametrize("text,plain", [
    ("세 시 십 분 전", "세 시 십 분"),
    ("9시 15분 전", "9시 15분"),
])
def test_the_two_directions_do_not_agree(text, plain):
    """The marked and unmarked readings of the same hour and minute land on
    different sides of that hour -- the pin that would fail if the clock
    were folded in the wrong direction."""
    assert start_end(text) != start_end(plain)


@pytest.mark.parametrize("text,expected", [
    ("오전 9시", minute_at(*TOMORROW, 9, 0)),
    ("오후 3시", minute_at(*TODAY, 15, 0)),
    ("오후 3:30", minute_at(*TODAY, 15, 30)),
    ("오전 9시 30분", minute_at(*TOMORROW, 9, 30)),
    ("오후 5시 45분", minute_at(*TODAY, 17, 45)),
    ("오후 열두 시", minute_at(*TOMORROW, 12, 0)),
])
def test_the_half_day_marker_leads_the_hour(text, expected):
    """오전 / 오후 stand BEFORE the hour, the opposite of English order."""
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("자정", minute_at(*TOMORROW, 0, 0)),
    ("정오", minute_at(*TOMORROW, 12, 0)),
])
def test_the_two_clock_landmarks(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("3시에", minute_at(*TOMORROW, 3, 0)),
    ("오후 3시 30분에", minute_at(*TODAY, 15, 30)),
    ("자정에", minute_at(*TOMORROW, 0, 0)),
])
def test_the_suffixed_particle_is_consumed_with_the_clock(text, expected):
    """에 is written onto the noun with no space at all, so the reading has
    to reach inside the token to find it."""
    assert start_end(text) == expected
    assert remainder(text) == ""


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_an_impossible_digit_clock_names_no_time(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["시", "분", "반", "시 분"])
def test_a_bare_clock_word_is_not_a_time(text):
    """시 is also a city and a poem; it reads as an hour only behind a
    numeral."""
    nomatch(text)
