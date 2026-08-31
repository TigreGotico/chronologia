"""The "<ordinal> to last" idiom must not be split into a range by its own
``to``.

``_extract_range`` scans the pre-fold token stream for the first ``to``
connector, and "second-to-last" carries one: the split produced a
``date_range`` from "the second" to "last friday at 5pm" at confidence 0.9,
outranking the correct ``weekday_ref`` at 0.8833. The answer came back one
week late with "the" as the remainder -- indistinguishable from a clean
parse. The forms without a trailing time ("... friday", "... friday at
noon") never split because their right-hand side failed to compose, which is
why the defect only surfaced on the composed ones.

Golds are independent calendar arithmetic. The anchor 2026-06-15 is a
Monday; June 2026's Fridays are the 5th, 12th, 19th and 26th, so the most
recent past Friday is the 12th and the second-to-last is the 5th. November
2026's Fridays are the 6th, 13th, 20th and 27th, so that month's
second-to-last Friday is the 20th.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

A = datetime(2026, 6, 15, 12, 0)


def _result(text, anchor=A):
    return extract_timespan(text, "en", anchor)


def _ymd(text, anchor=A):
    s = _result(text, anchor).span.start
    return (s.year, s.month, s.day)


@pytest.mark.parametrize("text,hour", [
    ("the second-to-last friday at 5pm", 17),
    ("the second-to-last friday morning", 6),
    ("the second-to-last friday evening", 18),
])
def test_composed_second_to_last_friday_is_june_5(text, hour):
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 6, 5)
    assert r.span.start.hour == hour


def test_second_to_last_friday_of_november_at_5pm():
    text = "the second-to-last friday of november at 5pm"
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 11, 20)
    assert r.span.start.hour == 17


def test_third_to_last_friday_at_5pm_is_may_29():
    text = "the third-to-last friday at 5pm"
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 5, 29)
    assert r.span.start.hour == 17


def test_spaced_spelling_reads_the_same_as_the_hyphenated_one():
    assert _ymd("the second to last friday at 5pm") == (2026, 6, 5)


@pytest.mark.parametrize("text", [
    "the second-to-last friday",
    "the second-to-last friday at noon",
])
def test_uncomposed_controls_unchanged(text):
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 6, 5)


@pytest.mark.parametrize("text", [
    "from monday to friday",
    "monday to friday",
    "monday-to-friday",
])
def test_genuine_weekday_range_still_binds(text):
    # the week after the Monday anchor: 2026-06-22 through 2026-06-26,
    # end-exclusive at 2026-06-27.
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert (r.span.start.year, r.span.start.month, r.span.start.day) \
        == (2026, 6, 22)
    assert (r.span.end.year, r.span.end.month, r.span.end.day) == (2026, 6, 27)


def test_genuine_clock_range_still_binds():
    r = _result("from 9 to 5")
    assert r is not None and r.remainder == ""
    assert r.span.start.hour == 9 and r.span.end.hour == 17


def test_fourth_to_last_friday_at_5pm_is_may_22():
    # the far edge of the idiom's -2..-4 bound: 06-12, 06-05, 05-29, 05-22.
    text = "the fourth-to-last friday at 5pm"
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 5, 22)
    assert r.span.start.hour == 17


def test_fifth_to_last_friday_at_5pm_is_out_of_bounds():
    # past the idiom's bound, so no ordinal reading exists and the qualifier
    # is stranded -- the same answer the guard-less engine gives, pinned as a
    # control rather than as desired behaviour.
    r = _result("the fifth-to-last friday at 5pm")
    assert r is not None and r.remainder == "the"
    assert _ymd("the fifth-to-last friday at 5pm") == (2026, 6, 12)


def test_multi_to_sentence_keeps_the_outer_range():
    # the idiom's own "to" is skipped, so the split lands on the real range
    # connector: second-to-last friday (06-05) through June's last friday
    # (06-26), end-exclusive 06-27.
    text = "from the second-to-last friday to the last friday of june"
    r = _result(text)
    assert r is not None and r.remainder == ""
    assert _ymd(text) == (2026, 6, 5)
    assert (r.span.end.year, r.span.end.month, r.span.end.day) == (2026, 6, 27)


@pytest.mark.xfail(reason="the tokenizer splits '2nd' into '2' + 'nd', so the "
                          "idiom's ordinal is not the connector's left "
                          "neighbour and neither the range guard nor the "
                          "weekday reading sees it",
                   strict=True)
def test_digit_ordinal_spelling_of_the_idiom():
    assert _ymd("the 2nd-to-last friday at 5pm") == (2026, 6, 5)
