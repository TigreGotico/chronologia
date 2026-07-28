"""A leading framing "on" before "the Nth of <month>" must keep the month.

Verified silent-wrong: with a leading "on", the parser resolved ONLY the
day-of-month ("on the 5th" -> next 5th) and STRANDED the explicit month
("of May") in the remainder, dropping it entirely.  "on" is a framing
preposition and must be transparent to the month binding: "on the 5th of
May" names the 5th of May exactly like "the 5th of May" does.

Reference values are hand-derived from the mission anchor (Tue 2017-06-27),
never pinned from the engine.  prefer-future applies: a month/day already
past this year rolls to next year.
"""
import pytest

from ._corpus import AstroDate, parse, span, start_end


# -- the fix: leading "on" keeps the named month --------------------------
@pytest.mark.parametrize("text, y, m, d", [
    ("on the 5th of May", 2018, 5, 5),        # May already past -> next year
    ("on the 5th of December", 2017, 12, 5),  # December still ahead this year
    ("meeting on the 5th of May", 2018, 5, 5),
    ("on the 1st of January", 2018, 1, 1),
    ("on the 20th of July", 2017, 7, 20),
])
def test_on_the_nth_of_month_binds_month(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e == AstroDate(y, m, d + 1)


def test_on_never_strands_the_month_word():
    # the whole date phrase is consumed; "of May" must NOT survive.
    _, rem = parse("on the 5th of May")
    assert "may" not in rem.lower()


# -- regression pins: the constructions that already worked stay identical -
def test_no_on_form_unchanged():
    # "the Nth of <month>" (no leading "on") -- must stay byte-identical.
    s, e = start_end("the 5th of May")
    assert (s, e) == (AstroDate(2018, 5, 5), AstroDate(2018, 5, 6))


def test_on_the_nth_without_month_is_next_day_of_month():
    # bare "on the Nth" (no month) -> next occurrence of that day-of-month.
    s, e = start_end("on the 5th")
    assert (s, e) == (AstroDate(2017, 7, 5), AstroDate(2017, 7, 6))


def test_on_month_day_unchanged():
    s, e = start_end("on May 5th")
    assert (s, e) == (AstroDate(2018, 5, 5), AstroDate(2018, 5, 6))


def test_on_weekday_unchanged():
    # "on Monday" -> the next Monday after Tue 2017-06-27 == 2017-07-03.
    s = span("on Monday")
    assert s.start == AstroDate(2017, 7, 3)
