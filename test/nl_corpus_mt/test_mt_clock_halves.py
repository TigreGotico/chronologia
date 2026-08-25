"""The clock changes anchor at the half hour.

Up to and including the half hour, Maltese names the hour it is already in and
ADDS the minutes with ``u`` ("and"): "Is-sitta u għaxra" is 06:10, "Is-sitta u
nofs" is 06:30.  Past the half hour it names the hour still COMING and
SUBTRACTS the minutes remaining with ``nieqes`` ("less"): "It-tmienja nieqes
kwart" is 07:45, not 08:15, and "L-għaxra nieqes ħamsa" is 09:55, not 10:05.

Both halves are pinned here against the other's reading, because the two are
numerically incompatible: a subtractive phrase read additively is off by
roughly twice the minute count, and lands in the wrong hour.

The anchor is a Wednesday at 13:04 and the locale prefers the future, so a
morning time has already passed today and is read as tomorrow's.
"""
import pytest

from ._corpus import ANCHOR, minute_at, parse, remainder, span


def _tomorrow(hh, mm):
    return minute_at(2027, 5, 13, hh, mm)


# -- first half of the hour: additive, off the hour already named -----------

@pytest.mark.parametrize("text,hh,mm", [
    ("is-sitta u ħamsa", 6, 5),
    ("is-sitta u għaxra", 6, 10),
    ("is-sitta u kwart", 6, 15),
    ("is-sitta u ħamsa u għoxrin", 6, 25),
    ("is-sitta u nofs", 6, 30),
    ("is-sebgħa u ħamsa", 7, 5),
    ("it-tmienja u għaxra", 8, 10),
    ("id-disgħa u kwart", 9, 15),
    ("l-għaxra u nofs", 10, 30),
    ("il-ħdax u kwart", 11, 15),
])
def test_before_the_half_hour_the_minutes_are_added(text, hh, mm):
    assert (span(text).start, span(text).end) == _tomorrow(hh, mm)


# -- second half of the hour: subtractive, off the hour still coming --------
# Worked examples from the sources: "It-tmienja nieqes kwart" == 07:45,
# "L-għaxra nieqes ħamsa" == 09:55.

@pytest.mark.parametrize("text,hh,mm", [
    ("it-tmienja nieqes kwart", 7, 45),
    ("l-għaxra nieqes ħamsa", 9, 55),
    ("is-sebgħa nieqes għaxra", 6, 50),
    ("is-sitta nieqes kwart", 5, 45),
    ("id-disgħa nieqes għoxrin", 8, 40),
    ("il-ħdax nieqes ħamsa", 10, 55),
    ("it-tnax nieqes kwart", 11, 45),
])
def test_after_the_half_hour_the_minutes_come_off_the_coming_hour(text, hh, mm):
    assert (span(text).start, span(text).end) == _tomorrow(hh, mm)


# -- the two halves are not interchangeable ---------------------------------

def test_the_subtractive_reading_is_not_the_additive_one():
    subtractive = span("it-tmienja nieqes kwart").start
    additive = span("it-tmienja u kwart").start
    assert subtractive.hour == 7 and subtractive.minute == 45
    assert additive.hour == 8 and additive.minute == 15


def test_a_bare_tens_after_u_reads_as_a_compound_number():
    # "u" joins a unit numeral to a tens word ("sitta u għoxrin" == 26), which
    # is the same word the clock uses additively.  The number wins, so a
    # minute count that is itself a bare tens cannot be spoken this way; the
    # spelling Maltese actually uses states the whole compound minute ("is-sitta
    # u ħamsa u għoxrin" == 06:25).
    assert parse("is-sitta u għoxrin") is None
    assert span("is-sitta u ħamsa u għoxrin").start.minute == 25


def test_the_direction_word_is_not_optional():
    # without a direction word the minute count has nothing to bind to, so the
    # bare hour is what is read and the count is left in the remainder.
    r = parse("is-sitta għaxra")
    assert r is not None and r[1] != ""


@pytest.mark.parametrize("text", [
    "is-sitta u nofs", "it-tmienja nieqes kwart", "l-għaxra nieqes ħamsa",
])
def test_a_clock_reading_consumes_its_whole_phrase(text):
    assert remainder(text) == ""


# -- the preposition contracts with the article -----------------------------

@pytest.mark.parametrize("bare,with_at", [
    ("is-sitta u nofs", "fis-sitta u nofs"),
    ("it-tmienja nieqes kwart", "fit-tmienja nieqes kwart"),
    ("l-għaxra nieqes ħamsa", "fl-għaxra nieqes ħamsa"),
])
def test_the_at_preposition_does_not_move_the_time(bare, with_at):
    assert span(bare).start == span(with_at).start


def test_the_morning_adverb_fixes_the_hour_in_the_am_half():
    assert (span("fis-sebgħa filgħodu").start,
            span("fis-sebgħa filgħodu").end) == _tomorrow(7, 0)


def test_the_evening_adverb_fixes_the_hour_in_the_pm_half():
    assert (span("fis-sebgħa filgħaxija").start,
            span("fis-sebgħa filgħaxija").end) == minute_at(
                2027, 5, 12, 19, 0)


# -- the three hours the weekday names take away ----------------------------

@pytest.mark.parametrize("text,weekday", [
    ("it-tnejn u għaxra", 0),
    ("it-tlieta u għaxra", 1),
    ("l-erbgħa nieqes għaxra", 2),
])
def test_two_three_and_four_oclock_read_as_weekdays(text, weekday):
    # it-Tnejn, it-Tlieta and l-Erbgħa are Monday, Tuesday and Wednesday AND
    # the articled cardinals two, three and four.  The weekday reading wins
    # and the minute phrase is left over: a clock time at those three hours
    # cannot be spelled with the article, and is refused rather than guessed.
    r = parse(text)
    assert r is not None
    assert r[0].start.weekday() == weekday
    assert r[1] != ""


def test_the_hours_without_a_weekday_homograph_still_read_as_clock_times():
    assert span("is-sitta u nofs").start.hour == 6
    assert span("il-ħdax u kwart").start.hour == 11


def test_midday_and_midnight():
    assert (span("nofsinhar").start.hour, span("nofsinhar").start.minute) == (12, 0)
    assert (span("nofsillejl").start.hour, span("nofsillejl").start.minute) == (0, 0)
    assert ANCHOR.hour == 13
