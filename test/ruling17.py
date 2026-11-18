"""Pins that rulings 17 and 23 moved: a lone hour takes the next twelve-hour reading.

An hour 1 to 12 said with no am/pm word and no part of the day is whichever of
h and h + 12 comes next at or after the anchor (ruling 17), and so is a digit
clock h:mm with an hour 1 to 11 and no leading zero (ruling 23).  A test that
pinned the old reading, the hour rolled to tomorrow, wraps its expected value
in ``moved``.  ``moved`` changes the value only for a test listed in
``ruling17_pins.txt`` or ``ruling23_pins.txt``; every other test, the
marked-hour rows among them, keeps its expected value.  The new value is date arithmetic on the anchor and the old
expected value.  It never reads chronologia.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from chronologia.astrodate import AstroDate, DateSpan

_LISTED = frozenset(
    line.rstrip("\n")
    for name in ("ruling17_pins.txt", "ruling23_pins.txt")
    for line in (Path(__file__).with_name(name)
                 .read_text(encoding="utf-8").splitlines())
    if line)


def listed():
    """Whether the running test is one whose pin ruling 17 moved."""
    node = os.environ.get("PYTEST_CURRENT_TEST", "").rsplit(" (", 1)[0]
    return node in _LISTED


def next_twelve(anchor, hour, minute=0, second=0):
    """The first of today h, today h + 12 and tomorrow h at or after ``anchor``."""
    anchor = anchor.replace(tzinfo=None)
    midnight = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
    tod = timedelta(hours=hour % 12, minutes=minute, seconds=second)
    return min(t for t in (midnight + tod,
                           midnight + tod + timedelta(hours=12),
                           midnight + tod + timedelta(days=1))
               if t >= anchor)


def moved(expected, anchor):
    """``expected`` as ruling 17 reads it, when the running test is listed."""
    if not listed():
        return expected
    if isinstance(expected, AstroDate):
        new = next_twelve(anchor, expected.hour, expected.minute,
                          expected.second)
        return expected.replace(year=new.year, month=new.month, day=new.day,
                                hour=new.hour)
    if isinstance(expected, datetime):
        return next_twelve(anchor, expected.hour, expected.minute,
                           expected.second)
    if isinstance(expected, DateSpan):
        return DateSpan(moved(expected.start, anchor),
                        moved(expected.end, anchor), expected.basis)
    if isinstance(expected, str):
        try:
            return moved(datetime.fromisoformat(expected), anchor).isoformat()
        except ValueError:
            return expected
    if isinstance(expected, bool):
        return expected
    if isinstance(expected, int):
        return next_twelve(anchor, expected).hour
    if isinstance(expected, tuple):
        ints = all(isinstance(x, int) and not isinstance(x, bool)
                   for x in expected)
        if ints and len(expected) == 2:
            new = next_twelve(anchor, expected[0], expected[1])
            return (new.hour, new.minute)
        if ints and len(expected) == 4:
            new = next_twelve(anchor, expected[2], expected[3])
            return (new.month, new.day, new.hour, new.minute)
        if ints and len(expected) == 5:
            new = next_twelve(anchor, expected[3], expected[4])
            return (new.year, new.month, new.day, new.hour, new.minute)
        return tuple(moved(x, anchor) for x in expected)
    return expected


def moved_date(date, clock, anchor):
    """A pinned ``(month, day)`` or ``(year, month, day)`` beside the pinned
    ``(hour, minute)`` that goes with it, when the running test is listed."""
    if not listed():
        return date
    new = next_twelve(anchor, clock[0], clock[1])
    return (new.month, new.day) if len(date) == 2 else (new.year, new.month, new.day)


def moved_dhm(dhm, anchor):
    """A pinned ``(day, hour, minute)``, when the running test is listed."""
    if not listed():
        return dhm
    new = next_twelve(anchor, dhm[1], dhm[2])
    return (new.day, new.hour, new.minute)
