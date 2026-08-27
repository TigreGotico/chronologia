"""The Saturday-first weekday cycle, and the week it implies.

Swahili names five of its weekdays by counting: juma ("week", from the Arabic
jum'a that also gives Friday its name Ijumaa) plus a numeral.  The count starts
on Saturday.  Jumamosi is juma + mosi (one), Jumapili is juma + pili (two) --
so Sunday is the day called two and Monday, called tatu (three), is the third.
Read with a Monday-first eye every one of those names lands two days early, and
the error is silent: Jumatatu would answer Wednesday and nothing would look
wrong about it.

The week the locale reckons with opens on the same Saturday.  English opens it
on Monday, so "wiki hii" and "this week" deliberately do NOT name the same
seven days, and both directions of that difference are pinned here.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, day, start_end


#: (surface, the date it names from the Wednesday anchor, its Monday-first
#: index).  The anchor is Wednesday 12 May 2027; a bare weekday reads forward.
CYCLE = [
    ("Jumatatu", (2027, 5, 17), 0),
    ("Jumanne", (2027, 5, 18), 1),
    ("Jumatano", (2027, 5, 19), 2),
    ("Alhamisi", (2027, 5, 13), 3),
    ("Ijumaa", (2027, 5, 14), 4),
    ("Jumamosi", (2027, 5, 15), 5),
    ("Jumapili", (2027, 5, 16), 6),
]


@pytest.mark.parametrize("word,date,_idx", CYCLE)
def test_a_bare_weekday_reads_forward(word, date, _idx):
    assert start_end(word) == day(*date)


@pytest.mark.parametrize("word,date,idx", CYCLE)
def test_the_weekday_lands_on_its_own_english_day(word, date, idx):
    """Each name must agree with the English weekday of the same index."""
    en = ["monday", "tuesday", "wednesday", "thursday", "friday",
          "saturday", "sunday"][idx]
    sw = extract_timespan(word, "sw", ANCHOR)
    en_r = extract_timespan(en, "en", ANCHOR)
    assert sw is not None and en_r is not None
    assert (sw[0].start, sw[0].end) == (en_r[0].start, en_r[0].end)


def test_the_juma_numeral_is_not_the_monday_first_index():
    """Jumatatu carries three and is Monday; Jumapili carries two and is Sunday.

    This is the pin the whole cycle turns on.  A locale that let the numeral
    inside the name choose the index would answer Wednesday for Jumatatu and
    Tuesday for Jumapili, both silently.
    """
    assert start_end("Jumatatu") == day(2027, 5, 17)     # a Monday
    assert start_end("Jumapili") == day(2027, 5, 16)     # a Sunday
    assert start_end("Jumamosi") == day(2027, 5, 15)     # a Saturday


# The agreement word TRAILS the weekday, as it trails every noun: "Jumatatu
# ijayo", never "ijayo Jumatatu".  Every weekday is class 9/10, so all seven
# take the same ijayo/iliyopita pair and none takes the class 3/4 ujao/uliopita
# that mwaka and mwezi take.

@pytest.mark.parametrize("word,nxt,prev", [
    ("Jumatatu", (2027, 5, 17), (2027, 5, 10)),
    ("Jumanne", (2027, 5, 18), (2027, 5, 11)),
    ("Jumatano", (2027, 5, 19), (2027, 5, 5)),
    ("Alhamisi", (2027, 5, 13), (2027, 5, 6)),
    ("Ijumaa", (2027, 5, 14), (2027, 5, 7)),
    ("Jumamosi", (2027, 5, 15), (2027, 5, 8)),
    ("Jumapili", (2027, 5, 16), (2027, 5, 9)),
])
def test_the_postposed_marker_selects_last_and_next(word, nxt, prev):
    assert start_end(f"{word} ijayo") == day(*nxt)
    assert start_end(f"{word} iliyopita") == day(*prev)


# -- the week starts on Saturday --------------------------------------------

def test_this_week_runs_saturday_to_saturday():
    assert start_end("wiki hii") == (day(2027, 5, 8)[0], day(2027, 5, 15)[0])


def test_next_week_runs_saturday_to_saturday():
    assert start_end("wiki ijayo") == (day(2027, 5, 15)[0], day(2027, 5, 22)[0])


def test_last_week_runs_saturday_to_saturday():
    assert start_end("wiki iliyopita") == (day(2027, 5, 1)[0],
                                           day(2027, 5, 8)[0])


@pytest.mark.parametrize("sw_text,en_text", [
    ("wiki hii", "this week"), ("wiki ijayo", "next week"),
    ("wiki iliyopita", "last week"),
])
def test_the_swahili_week_is_not_the_english_week(sw_text, en_text):
    """The counterpart of the pins above, asserted from the other side.

    English opens the week on Monday.  If a future change quietly reset this
    locale's week_start to monday every span above would still be a Saturday
    boundary in the test's own arithmetic only by accident, so the difference
    from English is pinned as a difference.
    """
    sw = extract_timespan(sw_text, "sw", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert sw is not None and en is not None
    assert sw[0].start != en[0].start, (
        f"{sw_text!r} answered the Monday-first week")
    assert sw[0].start.weekday() == 5, "the Swahili week must open on Saturday"


def test_a_week_offset_does_not_depend_on_the_week_start():
    """"wiki mbili zilizopita" is fourteen days, not two calendar weeks."""
    from datetime import timedelta
    from ._corpus import span
    assert span("wiki mbili zilizopita").start == ANCHOR - timedelta(days=14)
