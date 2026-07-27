"""The dot as a clock separator -- "HH.MM" British/European timetable style.

The 24-hour rail/timetable convention writes the wall clock with a dot instead
of a colon: "the 07.42 to London", "departs at 15.30".  The parser used to read
the dotted form as a *decimal number* ("07.42" -> 7.42), bind only the integer
hour to the clock and silently drop the minutes -- "at 07.42" resolved to 07:00.

The fix licenses the dotted clock in exactly the positions the colon clock is
already licensed -- a leading "at", a trailing am/pm meridiem, or a leading
article on the zero-padded timetable form -- and NOWHERE else.  A bare decimal
with no clock cue ("3.14", "7.42 meters", "version 7.42", "2.5 hours") keeps its
number/duration reading untouched; the dot is only a clock when something says
"clock" around it.

Anchor: Tuesday 2017-06-27 13:04.  ``prefer_future`` rolls a wall time already
past today to tomorrow.
"""
from ._corpus import parse, start, nomatch


# ---------------------------------------------------------------------------
# cued dotted clock -> HH:MM (the minutes survive)
# ---------------------------------------------------------------------------
# (text, y, mo, d, hh, mm)
_DOT_CLOCK = [
    ("at 07.42",            2017, 6, 28,  7, 42),  # 07:42 < 13:04 -> tomorrow
    ("7.42am",              2017, 6, 28,  7, 42),
    ("at 15.30",            2017, 6, 27, 15, 30),  # 15:30 > 13:04 -> today
    ("7.42pm",              2017, 6, 27, 19, 42),
    ("the train at 07.42",  2017, 6, 28,  7, 42),
    ("the 09.15 departure", 2017, 6, 28,  9, 15),
]


def test_dotted_clock_keeps_minutes():
    for text, y, mo, d, hh, mm in _DOT_CLOCK:
        s = start(text)
        assert (s.year, s.month, s.day, s.hour, s.minute) == (y, mo, d, hh, mm), \
            f"{text!r} -> {s!r}"


def test_train_remainder_survives():
    r = parse("the train at 07.42")
    assert r is not None and r[1] == "the train", r


# ---------------------------------------------------------------------------
# regression pins: the colon clock is unchanged, byte-identical
# ---------------------------------------------------------------------------
def test_colon_clock_unchanged():
    for text, hh, mm in [("at 7:42", 7, 42), ("at 07:42", 7, 42)]:
        s = start(text)
        assert (s.hour, s.minute) == (hh, mm), f"{text!r} -> {s!r}"


# ---------------------------------------------------------------------------
# regression pins: a bare decimal with NO clock cue stays a number, not a clock
# ---------------------------------------------------------------------------
def test_uncued_decimals_are_not_clocks():
    for text in ["3.14", "7.42 meters", "version 7.42", "7.42"]:
        nomatch(text)


def test_duration_unchanged():
    # "2.5 hours" is a duration, never 02:05 -- the dot fix must not touch it
    nomatch("2.5 hours")
