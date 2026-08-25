"""What this locale declines to answer, and why each refusal is the answer.

Every case here is an omission with a reason.  A locale that guessed at any of
them would return a confident wrong span for text a Macedonian speaker writes,
which is worse than returning nothing, so each refusal is pinned as hard as the
readings that do ship.
"""
import pytest

from ._corpus import nomatch, parse, span, start_end, day


# -- no "since" --------------------------------------------------------------
# "од X до Y" is the attested range and it answers correctly, because до alone
# already closes it and the span needs nothing from од.  A standalone temporal
# "since Monday" is a different construction and no source consulted names one
# for Macedonian, so од carries no marker of its own at all: giving it one
# would hand every bare "од X" an open-ended reading reaching from X to now,
# which is precisely the meaning left unconfirmed.  од stays in the remainder.

@pytest.mark.parametrize("text", [
    "од понеделник", "од јуни", "од 5 јуни", "од вчера",
])
def test_a_bare_from_is_not_a_since(text):
    r = parse(text)
    assert r is None or r[1] != "", (
        f"{text!r} was answered as an open-ended range with од consumed")


def test_the_range_that_does_ship_still_answers_correctly():
    assert start_end("од 5 јуни до 8 јуни") == (day(2027, 6, 5)[0],
                                                day(2027, 6, 9)[0])
    assert start_end("од понеделник до петок") == (day(2027, 5, 17)[0],
                                                   day(2027, 5, 22)[0])


# -- no century, no millennium ----------------------------------------------
# CLDR carries no century or millennium field for Macedonian and no other
# source consulted gives their counted plurals, so neither unit ships and no
# plural is invented for either.

@pytest.mark.parametrize("text", [
    "пред два века", "пред 2 века", "пред 5 векови", "пред еден век",
    "милениум", "пред еден милениум", "пред два милениуми",
])
def test_the_century_and_the_millennium_are_not_shipped(text):
    nomatch(text)


# -- no minutes-to-the-hour clock -------------------------------------------
# Two sources written to be exhaustive -- a style guide on how the time is
# said, and a grammar cataloguing every sense of без -- show the clock counting
# forward and only forward.  A subtractive reading is therefore not merely
# unconfirmed, it is contradicted, and is refused rather than borrowed from
# neighbouring Bulgarian.

@pytest.mark.parametrize("text", [
    "без петнаесет девет", "девет без петнаесет", "без пет десет",
])
def test_bez_is_not_a_clock_word(text):
    r = parse(text)
    assert r is None or r[1] != ""


# -- no spelled day of the month --------------------------------------------
# The date line CLDR states is written with a digit for the day.  Which form a
# spelled ordinal takes in front of a month name is not given by any source
# consulted, so the ordinal is not read as a day and the phrase falls back to
# the whole month rather than a guessed one of its days.

@pytest.mark.parametrize("text", ["први мај", "петти мај", "трети јуни"])
def test_a_spelled_ordinal_is_not_read_as_a_day(text):
    r = parse(text)
    assert r is not None
    assert r[1] != "", f"{text!r} consumed the ordinal without a source for it"
    assert r[0].start.day == 1 and r[0].end.day == 1


def test_a_digit_day_is_unaffected():
    assert start_end("5 јуни 2027") == day(2027, 6, 5)


# -- the singular недела is Sunday, not a week ------------------------------
# CLDR spells the week field седмица and gives недела as Sunday; the two senses
# collide only on the singular, where the weekday reading is the one that
# ships.  The plural недели counts weeks, where no weekday reading competes.

def test_the_singular_is_the_weekday():
    assert start_end("следната недела") == day(2027, 5, 16)


def test_the_plural_counts_weeks():
    s = span("пред 2 недели")
    assert (s.start.year, s.start.month, s.start.day) == (2027, 4, 28)


# -- no invented day-part bands ---------------------------------------------
# CLDR draws five bands plus two points for Macedonian.  Words naming other
# stretches of the day are not given band boundaries nobody stated.

@pytest.mark.parametrize("text", ["зора", "самрак", "предзорје"])
def test_no_band_is_invented(text):
    nomatch(text)
