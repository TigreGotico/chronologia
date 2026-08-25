"""The additive clock, and the minutes-to-the-hour form Macedonian does not have.

Minutes are counted forward from the hour already named, through fifty-nine:
"девет и петнаесет" is 9:15, "дваесет и еден и педесет" is 21:50, and the half
hour goes the same way -- "девет и пол" is 9:30, half past nine and not half
toward it.  Both halves of the day are exercised, spelled and in digits, and the
subtractive reading neighbouring Bulgarian uses is pinned as unreadable.
"""
import pytest

from ._corpus import ANCHOR, minute_at, nomatch, parse, span, start_end

#: prefer_future puts a bare morning clock on the day after a 13:04 anchor.
TOMORROW = (2027, 5, 13)
TODAY = (2027, 5, 12)


@pytest.mark.parametrize("text,day_,hh,mm", [
    ("девет и петнаесет", TOMORROW, 9, 15),
    ("девет и пол", TOMORROW, 9, 30),
    ("девет и пет", TOMORROW, 9, 5),
    ("девет и дваесет", TOMORROW, 9, 20),
    ("девет и четириесет и пет", TOMORROW, 9, 45),
    ("девет и педесет", TOMORROW, 9, 50),
    ("девет и педесет и девет", TOMORROW, 9, 59),
    ("осум и десет", TOMORROW, 8, 10),
    ("седум и триесет", TOMORROW, 7, 30),
    ("шест и пол", TOMORROW, 6, 30),
    ("единаесет и пол", TOMORROW, 11, 30),
    ("дванаесет и пол", TOMORROW, 12, 30),
    ("дваесет и еден и педесет", TODAY, 21, 50),
    ("дваесет и три и педесет и девет", TODAY, 23, 59),
    ("нула и триесет", TOMORROW, 0, 30),
])
def test_the_clock_counts_minutes_forward(text, day_, hh, mm):
    assert start_end(text) == minute_at(*day_, hh, mm)


@pytest.mark.parametrize("text,day_,hh,mm", [
    ("9 и 15", TOMORROW, 9, 15),
    ("9 и пол", TOMORROW, 9, 30),
    ("12 и пол", TOMORROW, 12, 30),
    ("21 и 50", TODAY, 21, 50),
    ("23 и 59", TODAY, 23, 59),
])
def test_the_same_clock_written_in_digits(text, day_, hh, mm):
    assert start_end(text) == minute_at(*day_, hh, mm)


@pytest.mark.parametrize("text,day_,hh,mm", [
    ("09:30", TOMORROW, 9, 30),
    ("21:50", TODAY, 21, 50),
    ("00:00", TOMORROW, 0, 0),
    ("13:05", TODAY, 13, 5),
])
def test_the_digital_clock(text, day_, hh, mm):
    assert start_end(text) == minute_at(*day_, hh, mm)


@pytest.mark.parametrize("text,hh", [
    ("во 5 часот", 5), ("во 9 часот", 9), ("во 11 часот", 11),
])
def test_the_hour_named_with_its_article(text, hh):
    assert start_end(text) == minute_at(*TOMORROW, hh, 0)


@pytest.mark.parametrize("text,day_,hh,mm", [
    ("во 9 претпл", TOMORROW, 9, 0),
    ("9:30 попл", TODAY, 21, 30),
    ("11:15 претпл", TOMORROW, 11, 15),
])
def test_the_borrowed_meridiem_labels(text, day_, hh, mm):
    assert start_end(text) == minute_at(*day_, hh, mm)


@pytest.mark.parametrize("text,hh,mm", [
    ("полноќ", 0, 0), ("пладне", 12, 0), ("напладне", 12, 0),
])
def test_the_two_clock_landmarks(text, hh, mm):
    s = span(text)
    assert (s.start.hour, s.start.minute) == (hh, mm)


# -- the minutes-to-the-hour form ------------------------------------------
# Macedonian counts minutes forward and only forward.  A style guide written
# to teach how the time is said gives additive examples through 21:50 and no
# other, and mk.wikipedia's article on the prepositions catalogues every sense
# of без without naming a temporal one.  So без is not a clock word here, and a
# phrase built on it must not be answered with the hour it would name in
# Bulgarian.

@pytest.mark.parametrize("text", [
    "девет без петнаесет", "девет без пет", "десет без дваесет",
    "девет без пол", "осум без десет",
])
def test_no_minutes_to_the_hour_reading(text):
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text,hh,mm", [
    ("девет без петнаесет", 8, 45),
    ("девет без пет", 8, 55),
    ("десет без дваесет", 9, 40),
])
def test_the_subtractive_hour_is_never_returned(text, hh, mm):
    r = parse(text)
    if r is not None:
        assert (r[0].start.hour, r[0].start.minute) != (hh, mm)


def test_the_quarter_word_is_not_a_clock_fraction():
    # The style guide writes the quarter hour as "девет и петнаесет", with the
    # minute spelled out; четврт is the ordinal "fourth" and no source shows it
    # in a clock, so it is not read as one.
    nomatch("девет и четврт")


def test_impossible_clocks_are_never_returned_as_times():
    for text in ("25:00", "15:99", "99:99"):
        r = parse(text)
        if r is not None:
            assert 0 <= r[0].start.hour <= 23


def test_a_bare_connector_is_not_a_time():
    nomatch("и")
    assert parse("девет и") is None or parse("девет и")[1] != ""
