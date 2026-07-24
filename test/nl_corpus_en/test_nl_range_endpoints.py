"""Wave 1 -- range endpoints: bare hours, scoped leads, zones, far futures.

An explicit ``from``/``between`` lead frames its two operands as the ends of
one interval.  That framing is what licenses a bare numeral to be read as an
*hour* ("from 9 to 5" is a working day) and what decides which meridiem each
end takes -- while, with no lead in front of it, "ten to five" stays the
subtractive clock reading English actually means.

Anchor is Tuesday 2017-06-27 13:04, so 09:00 has already gone by and a bare
morning hour lands on the Wednesday.
"""
import time
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start_end


def _dt(day, hour, minute=0):
    return AstroDate(2017, 6, day, hour, minute)


# -- a bare numeral under an explicit lead is an hour ----------------------
# "from 9 to 5" used to fall through to the subtractive clock and resolve to a
# one-minute span at 04:51, with the "from" orphaned to the remainder.

@pytest.mark.parametrize("text,s,e", [
    ("from 9 to 5", _dt(28, 9), _dt(28, 17, 1)),
    ("from 9 to 5pm", _dt(28, 9), _dt(28, 17, 1)),
    ("from 9 to 5 pm", _dt(28, 9), _dt(28, 17, 1)),
    ("from 9am to 5pm", _dt(28, 9), _dt(28, 17, 1)),
    ("from 09:00 to 17:00", _dt(28, 9), _dt(28, 17, 1)),
    ("from 2 to 4", _dt(28, 2), _dt(28, 4, 1)),
    ("between 3 and 5 pm", _dt(27, 15), _dt(27, 17, 1)),
])
def test_bare_hour_range(text, s, e):
    assert start_end(text) == (s, e)


def test_bare_hour_range_keeps_the_lead_out_of_the_remainder():
    assert parse("from 9 to 5")[1] == ""


@pytest.mark.parametrize("text,rem", [
    ("the shop is open from 9 to 5", "the shop is open"),
    ("I work from 9 to 5 pm", "I work"),
])
def test_bare_hour_range_with_context(text, rem):
    got, remainder = parse(text)
    assert (got.start, got.end) == (_dt(28, 9), _dt(28, 17, 1))
    assert remainder == rem


def test_bare_hour_range_on_a_named_day():
    # the dateless end is placed on the day the other end names
    got = span("from 9 to 5 on thursday")
    assert (got.start, got.end) == (_dt(29, 9), _dt(29, 17, 1))


# -- the subtractive clock survives where no lead frames a range -----------
# This reading is correct English and the fix is about precedence, not removal.

@pytest.mark.parametrize("text,s", [
    ("ten to five", _dt(28, 4, 50)),
    ("quarter to five", _dt(28, 4, 45)),
    ("nine to five", _dt(28, 4, 51)),
    ("five to eight", _dt(28, 7, 55)),
])
def test_subtractive_clock_without_a_lead(text, s):
    assert start_end(text) == (s, s + timedelta(minutes=1))


def test_from_quarter_to_five_is_still_the_clock():
    # "quarter" is no hour, so the range refuses and the clock reading wins
    assert span("from quarter to five").start == _dt(28, 4, 45)


# -- a scoping qualifier stays inside the range ----------------------------
# "next week from monday to friday" used to land a week late, because the
# lead scan started at token 0 and "week from monday" was read as a week.

def test_next_week_from_monday_to_friday():
    # anchor Tue 2017-06-27; next week is Mon 07-03 .. Sun 07-09
    assert start_end("next week from monday to friday") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 8))


def test_plain_monday_to_friday_is_unchanged():
    assert start_end("from monday to friday") == (
        AstroDate(2017, 7, 3), AstroDate(2017, 7, 8))


# -- a zone named once governs both ends -----------------------------------
# These raised TypeError (naive vs aware comparison) from a public entry point
# documented as never raising.

@pytest.mark.parametrize("text", [
    "from noon to 3:30 utc+2",
    "from 1pm to 3pm utc+2",
    "from noon to 3 pm gmt",
    "between 3:30 and 5:00 utc+2",
    "from monday to friday at 3:30 utc+2",
    "from 9 to 5 utc+2",
])
def test_zoned_range_never_raises(text):
    parse(text)          # must not raise; None is an acceptable answer


def test_zoned_range_reads_both_ends_on_the_named_zone():
    got = span("from 1pm to 3pm utc+2")
    assert got.start.tzinfo is not None
    assert got.start.utcoffset() == got.end.utcoffset() == timedelta(hours=2)
    assert (got.start.hour, got.end.hour) == (13, 15)


# -- a far-future range resolves by arithmetic, not by stepping ------------
# The cycle roll used to advance one day per iteration from the clock's anchor
# day to the left endpoint, so the utterance chose the cost via its year:
# "from june 12 9999 to 3:30" took ~45 s inside a synchronous intent parse.

@pytest.mark.parametrize("text", [
    "from june 12 9999 to 3:30",
    "from june 12 3000 to 3:30",
    "from june 12 9999 to monday",
])
def test_far_future_range_is_fast(text):
    t0 = time.monotonic()
    parse(text)
    assert time.monotonic() - t0 < 1.0


def test_far_future_clock_range_still_lands_on_the_left_endpoint_day():
    got = span("from june 12 9999 to 3:30")
    assert got.start == AstroDate(9999, 6, 12)
    assert got.end == AstroDate(9999, 6, 12, 3, 31)


def test_far_future_weekday_range_rolls_to_the_next_weekday():
    # 9999-06-12 is a Saturday, so the range runs to the following Monday
    got = span("from june 12 9999 to monday")
    assert got.start == AstroDate(9999, 6, 12)
    assert got.end == AstroDate(9999, 6, 15)


# -- non-regressions the range machinery already got right -----------------

@pytest.mark.parametrize("text,s,e", [
    ("between june 5th and june 12th",
     AstroDate(2018, 6, 5), AstroDate(2018, 6, 13)),
    ("from 2026-W10 to 2026-W12",
     AstroDate(2026, 3, 2), AstroDate(2026, 3, 23)),
    ("from 10 pm to 2 am", _dt(27, 22), _dt(28, 2, 1)),
])
def test_range_non_regressions(text, s, e):
    assert start_end(text) == (s, e)
