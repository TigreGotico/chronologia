# -*- coding: utf-8 -*-
"""What this locale declines to read, and why each refusal is the right answer.

Every case here is a phrase for which a plausible reading exists and no source
settles it.  Answering the plausible one would hand a caller a confident span
built on a guess, which is worse than answering nothing: nothing is visibly
absent, a wrong span is not.
"""
import pytest

from ._corpus import nomatch, parse, start_end


@pytest.mark.parametrize("text", [
    "இரண்டு திங்கள்",
    "மூன்று திங்கள்",
    "ஆறு திங்கள்",
])
def test_a_count_before_thingal_refuses(text):
    """திங்கள் is Monday, the moon, the month and -- obsoletely -- the week.
    A count in front of it can only be a span of months; nobody counts Mondays
    that way.  This locale reads the month unit as மாதம், CLDR's own wording,
    and ships no month sense for திங்கள், so the count vetoes the weekday
    reading rather than answering one specific Monday to a question about
    months.  Declining the false weekday reading is not the same as asserting
    the unshipped month one, which stays unavailable."""
    nomatch(text)


def test_thingal_alone_is_still_monday():
    """The veto is scoped to the counted phrase.  Bare திங்கள் carries no
    count, so the weekday reading is the only one on offer and it stands --
    2027-05-12 is a Wednesday, so the coming Monday is the 17th."""
    s = start_end("திங்கள்")[0]
    assert (s.year, s.month, s.day) == (2027, 5, 17)


@pytest.mark.parametrize("text,days", [
    ("இரண்டு மாதங்களுக்கு முன்", 2),
    ("ஆறு மாதங்களில்", 6),
])
def test_the_month_unit_is_maadham_and_it_works(text, days):
    """The refusal above costs nothing a speaker actually needs: the unit word
    CLDR uses carries every counted-month reading."""
    assert parse(text) is not None


@pytest.mark.parametrize("text", [
    "ஒன்பதே முக்கால்",
    "ஒன்பது மணி முக்கால்",
    "மூன்று மணி முக்கால்",
])
def test_three_quarters_on_the_clock_refuses(text):
    """அரை and கால் are worked out with numbers by the sources; முக்கால் is
    not.  Reading it as three quarters past the named hour is an analogy from
    the other two, and an analogy is not evidence.  The whole phrase is
    withdrawn, numeral included, so the hour cannot survive as a bare day of
    the month either."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி",
    "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி",
])
def test_the_tamil_solar_months_do_not_resolve(text):
    """The Tamil solar calendar is a full second register and its month names
    are live.  They are not the month-1-to-12 equivalents of the Gregorian
    list: each straddles a Gregorian month boundary, and turning one into a
    date needs calendar arithmetic no source consulted closes.  Recognising
    them without that arithmetic would mean answering a date a month wide and
    a fortnight off, so none is shipped."""
    nomatch(text)


@pytest.mark.parametrize("text", ["மணி", "மணிக்கு", "நிமிடம்", "கால்",
                                  "அரை", "முக்கால்", "மேல்", "குறைவு"])
def test_a_bare_clock_word_names_no_time(text):
    """மணி is "bell" before it is "o'clock", and கால் is the ordinary word for
    a leg.  Both read as clock words only beside a numeral, which is what the
    fold requires; on their own they bind nothing."""
    nomatch(text)


@pytest.mark.parametrize("text", ["நாள்", "வாரம்", "மாதம்", "ஆண்டு",
                                  "மணிநேரம்", "விநாடி"])
def test_a_bare_unit_without_a_count_is_not_an_offset(text):
    """A unit noun with nothing counting it names no stretch of time."""
    nomatch(text)


@pytest.mark.parametrize("text", ["ஞாயிறு", "வெள்ளி", "செவ்வாய்", "சனி"])
def test_the_weekday_names_are_planet_names_and_still_read_as_weekdays(text):
    """ஞாயிறு is Sunday and the sun, வெள்ளி is Friday and Venus, செவ்வாய் is
    Tuesday and Mars, சனி is Saturday and Saturn -- the whole set doubles as
    the planets, so astronomical prose is a known false-positive field.  The
    weekday sense is the everyday one and is the one shipped; the collision is
    recorded here rather than resolved, because nothing inside a phrase
    separates the two senses."""
    assert parse(text) is not None


def test_a_bare_two_digit_number_is_not_a_year():
    """The four-digit guard: 26 is a day of the month or a count, never 2026."""
    nomatch("26")
