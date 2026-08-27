# -*- coding: utf-8 -*-
"""What this locale declines to read, and why each refusal beats a guess.

Every case here has two live readings and nothing inside the phrase to choose
between them.  Answering one of them would be silently wrong in half the uses
and would look exactly like a correct answer.
"""
import pytest

from ._corpus import nomatch, start_end, band


@pytest.mark.parametrize("text", [
    "หกโมง", "เจ็ดโมง", "สิบโมง", "สองโมง",
])
def test_a_bare_hour_word_is_ambiguous_between_the_half_days(text):
    """หกโมงเช้า is 06:00 and หกโมงเย็น is 18:00.  Strip the day-part word and
    the sources disagree about which half-day a bare โมง phrase names -- one
    glosses bare หกโมงห้านาที as an evening reading, another puts bare หกโมง
    in the morning.  Nothing in the phrase separates them."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "หกโมงห้านาที", "แปดโมงครึ่ง", "เจ็ดโมงยี่สิบ",
])
def test_the_minute_tail_does_not_rescue_a_bare_hour_word(text):
    """A count after the hour fixes the minutes, never the half-day, so the
    whole phrase -- minutes included -- is withdrawn rather than half-read."""
    nomatch(text)


@pytest.mark.parametrize("text", ["บ่ายสี่โมง", "บ่ายห้าโมง", "สี่โมงเย็น",
                                  "ห้าโมงเย็น"])
def test_the_disputed_late_afternoon_is_not_assigned(text):
    """The sources disagree about which word covers 16:00-18:59: one gives
    16:00-18:00 to โมงเย็น and starts ทุ่ม at 19:00, another runs บ่าย to
    18:00, a third draws the afternoon quarter as 13:00-18:59.  The band is
    omitted rather than awarded to a winner."""
    nomatch(text)


@pytest.mark.parametrize("text", ["หนึ่งโมงเช้า", "สองโมงเช้า", "ห้าโมงเช้า"])
def test_the_morning_hours_the_two_numberings_collide_on_are_not_read(text):
    """Every worked morning example reads N โมงเช้า as N o'clock, which is
    only free of a competing reading from six onwards: the traditional
    six-hour cycle numbers the same 07:00-11:00 as one through five."""
    nomatch(text)


@pytest.mark.parametrize("text", ["หกทุ่ม", "เจ็ดทุ่ม", "ตีหก", "ตีเจ็ด"])
def test_the_sixth_hour_of_a_quarter_has_its_own_name(text):
    """The quarters run one to five and the sixth hour is named separately
    (ย่ำรุ่ง at dawn, ย่ำค่ำ at dusk), so counting past five is not a form the
    language has."""
    nomatch(text)


def test_a_refused_clock_does_not_decay_into_its_day_part_word():
    """บ่าย is also the afternoon band.  Withdrawing only the numeral would
    leave the band behind and answer four hours for a phrase that named one
    minute -- so the whole phrase goes, day-part word included."""
    nomatch("บ่ายสี่โมง")
    # the bare band word on its own still reads
    assert start_end("บ่าย") == band(2027, 5, 12, (12, 0), (16, 0))


def test_the_sunday_word_is_never_read_as_the_week():
    """อาทิตย์ is both Sunday and the week.  The locale gives the surface to
    Sunday alone and ships สัปดาห์ for the week, so a count on อาทิตย์ counts
    Sundays and can never quietly answer a stretch of weeks instead."""
    weeks = start_end("สองสัปดาห์ที่ผ่านมา")
    sundays = start_end("สองอาทิตย์ที่ผ่านมา")
    assert sundays != weeks
    # a single day, and that day a Sunday
    assert (sundays[1] - sundays[0]).days == 1
    assert sundays[0].weekday() == 6


def test_a_bare_four_digit_year_is_not_read_as_a_buddhist_one():
    """A bare Thai year identifies no era -- CLDR's own long and full date
    patterns for th carry the era field for exactly that reason -- so it is
    read as Common Era and the พ.ศ. marker is what selects the other."""
    from ._corpus import start
    assert start("2568").year == 2568
