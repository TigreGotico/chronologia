"""``ordinal_cap``: the reason a month or a year holds no n-th weekday, day, week or business day.

The expected values come from the calendar worked by hand.  1 January 2027 is a
Friday, so 1 May 2027 is a Saturday and 1 February 2027 is a Monday; 2027 has
365 days, so it holds 53 Fridays and 52 of every other weekday.  2024 is a
leap year that starts on a Monday, so it holds 262 weekdays.  May 2023 starts on
a Monday and has 31 days (23 weekdays); April 2019 starts on a Monday and has 30
days (22 weekdays); February 2016 starts on a Monday and has 29 days (21
weekdays).
"""
import pytest

from chronologia.extract.impossible import ordinal_cap

MON, TUE, FRI, SUN = 0, 1, 4, 6

# A named year means the caller searched that period and found no such ordinal.
# May 2027 holds 5 Mondays (3, 10, 17, 24, 31), so its 6th is the first that is
# missing; February 2027 holds 4 of each weekday; 2027 holds 52 Mondays.
_NAMED_PERIOD = [
    (6, MON, 5, 2027, "May 2027 has no 6th Monday"),
    (-6, MON, 5, 2027, "May 2027 has no 6th to last Monday"),
    (5, TUE, 5, 2027, "May 2027 has no 5th Tuesday"),
    (5, MON, 2, 2027, "February 2027 has no 5th Monday"),
    (5, MON, 2, 2028, "February 2028 has no 5th Monday"),
    (53, MON, None, 2027, "2027 has no 53rd Monday"),
    (53, FRI, None, 2028, "2028 has no 53rd Friday"),
    (-53, MON, None, 2027, "2027 has no 53rd to last Monday"),
    # a unit other than a weekday is refused the same way
    (24, "business day", 5, 2026, "May 2026 has no 24th business day"),
    (263, "business day", None, 2027, "2027 has no 263rd business day"),
    (6, "weekend", 5, 2027, "May 2027 has no 6th weekend"),
    (32, "day", 1, 2027, "January 2027 has no 32nd day"),
    (54, "week", None, 2026, "2026 has no 54th week"),
]


@pytest.mark.parametrize("n, unit, month, year, reason", _NAMED_PERIOD)
def test_a_named_year_always_gives_the_reason(n, unit, month, year, reason):
    per = "month" if month else "year"
    assert ordinal_cap(n, unit, month, year, per=per) == reason


_ANY_PERIOD = [
    # a month holds at most 5 of one weekday and 5 weekends
    (5, MON, None, "month", None),
    (6, MON, None, "month", "a month has no 6th Monday"),
    (-6, SUN, None, "month", "a month has no 6th to last Sunday"),
    (5, "weekend", None, "month", None),
    (6, "weekend", 5, "month", "May has no 6th weekend"),
    # a month holds at most 31 days, 6 weeks (a 31-day month from a Saturday) and
    # 23 weekdays (May 2023)
    (31, "day", None, "month", None),
    (32, "day", None, "month", "a month has no 32nd day"),
    (6, "week", None, "month", None),
    (7, "week", None, "month", "a month has no 7th week"),
    (23, "business day", None, "month", None),
    (24, "business day", None, "month", "a month has no 24th business day"),
    # per month: 31 days except February (29 in a leap year) and the 30-day months;
    # weekdays at most 22 in April, 21 in February (2016)
    (29, "day", 2, "month", None),
    (30, "day", 2, "month", "February has no 30th day"),
    (30, "day", 4, "month", None),
    (31, "day", 4, "month", "April has no 31st day"),
    (22, "business day", 4, "month", None),
    (23, "business day", 4, "month", "April has no 23rd business day"),
    (21, "business day", 2, "month", None),
    (22, "business day", 2, "month", "February has no 22nd business day"),
    (23, "business day", 5, "month", None),
    # a year holds at most 53 of one weekday, 262 weekdays (2024), 366 days,
    # 53 ISO weeks and 12 months
    (53, FRI, None, "year", None),
    (54, FRI, None, "year", "a year has no 54th Friday"),
    (262, "business day", None, "year", None),
    (263, "business day", None, "year", "a year has no 263rd business day"),
    (366, "day", None, "year", None),
    (367, "day", None, "year", "a year has no 367th day"),
    (53, "week", None, "year", None),
    (54, "week", None, "year", "a year has no 54th week"),
    (12, "month", None, "year", None),
    (13, "month", None, "year", "a year has no 13th month"),
    # a unit the period cannot count is refused at once
    (1, "decade", None, "year", "a year has no 1st decade"),
]


@pytest.mark.parametrize("n, unit, month, per, reason", _ANY_PERIOD)
def test_an_unnamed_period_is_capped_at_the_most_any_such_period_holds(
        n, unit, month, per, reason):
    assert ordinal_cap(n, unit, month, per=per) == reason


def test_a_zeroth_ordinal_is_refused_only_when_asked():
    assert ordinal_cap(0, MON) is None
    assert ordinal_cap(0, MON, zero=True) == "a month has no 0th Monday"
    assert ordinal_cap(0, "business day", 5, zero=True) == "May has no 0th business day"
