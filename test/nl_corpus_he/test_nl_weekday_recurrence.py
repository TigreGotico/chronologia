# -*- coding: utf-8 -*-
"""Every weekday as a Hebrew recurrence, and the "every day" it is not.

Hebrew names its weekdays by ordinal number -- יום ראשון is the first day
(Sunday) and יום שני the second (Monday), the seventh keeping its own name
שבת -- so every weekday rule opens with the same day noun the bare "every
day" rule does.  "כל יום שני" is every Monday; only the bare "כל יום" is
FREQ=DAILY.

Monday is the case the day noun has to carry on its own: שני is at once the
ordinal "second" and the construct cardinal "two", so "כל שני ימים" (every
two days) and "כל יום שני" (every Monday) differ by nothing but the words
around שני.  Both readings are asserted here.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "he"

# the full יום form, its ב-prefixed variant and the letter abbreviation, for
# each day of the week.
_WEEKDAYS = [
    ('ראשון', 'א', 'SU'),
    ('שני', 'ב', 'MO'),
    ('שלישי', 'ג', 'TU'),
    ('רביעי', 'ד', 'WE'),
    ('חמישי', 'ה', 'TH'),
    ('שישי', 'ו', 'FR'),
]


@pytest.mark.parametrize("name,letter,byday", _WEEKDAYS)
def test_every_weekday(name, letter, byday):
    got = extract_recurrence(f'כל יום {name}', LANG)
    assert got is not None, f'כל יום {name} did not parse as a recurrence'
    assert got[0].to_string() == f'FREQ=WEEKLY;BYDAY={byday}'
    assert got[1] == ''


@pytest.mark.parametrize("name,letter,byday", _WEEKDAYS)
def test_every_weekday_abbreviated(name, letter, byday):
    """The calendar abbreviation יום א׳ .. יום ו׳ reads as the same day."""
    got = extract_recurrence(f'כל יום {letter}', LANG)
    assert got is not None, f'כל יום {letter} did not parse as a recurrence'
    assert got[0].to_string() == f'FREQ=WEEKLY;BYDAY={byday}'


@pytest.mark.parametrize("text", ['כל שבת', 'כל יום שבת', 'כל יום ש'])
def test_every_saturday(text):
    got = extract_recurrence(text, LANG)
    assert got is not None, f'{text!r} did not parse as a recurrence'
    assert got[0].to_string() == 'FREQ=WEEKLY;BYDAY=SA'


def test_bare_every_day_is_still_daily():
    got = extract_recurrence('כל יום', LANG)
    assert got is not None
    assert got[0].to_string() == 'FREQ=DAILY'
    assert got[1] == ''


@pytest.mark.parametrize("text,rrule", [
    ('כל שני ימים', 'FREQ=DAILY;INTERVAL=2'),
    ('כל שני שבועות', 'FREQ=WEEKLY;INTERVAL=2'),
])
def test_counted_interval_is_not_monday(text, rrule):
    """שני counting a following noun is the cardinal "two", not Monday."""
    got = extract_recurrence(text, LANG)
    assert got is not None, f'{text!r} did not parse as a recurrence'
    assert got[0].to_string() == rrule


def test_bare_monday_with_nothing_to_count():
    """With no noun after it שני cannot be the cardinal, so it is Monday."""
    got = extract_recurrence('כל שני', LANG)
    assert got is not None
    assert got[0].to_string() == 'FREQ=WEEKLY;BYDAY=MO'


@pytest.mark.parametrize("text", [
    '',
    '   ',
    'כל',
    'יום',
    'שני',
    'כל יום ז',
    'כל יום שנילישי',
    'לורם איפסום',
    'כל יום !!! ???',
    'ככל שיום שני',
])
def test_garbage_never_raises(text):
    """Nothing here is a recurrence, and nothing here may explode."""
    got = extract_recurrence(text, LANG)
    assert got is None or got[0].to_string()
