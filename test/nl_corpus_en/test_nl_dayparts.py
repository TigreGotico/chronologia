"""Dayparts -- the coarse portions of a day a speaker names instead of a
clock time: "this morning", "tomorrow afternoon", "friday night".

The engine's daypart windows (hand-confirmed, all on the same civil day
except NIGHT, which runs from 21:00 into 06:00 of the following morning):

    morning    06:00 - 12:00
    afternoon  12:00 - 18:00
    evening    18:00 - 21:00
    night      21:00 - 06:00 (+1 day)

A bare weekday resolves to its next STRICTLY-future occurrence from the
Tuesday 2017-06-27 anchor (weekday index 1); "today"/"tomorrow"/"yesterday"
shift the base civil day by 0/+1/-1.  Every expected edge below is derived by
independent Python arithmetic against the anchor -- never from the parser.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start_end


# -- daypart windows as (start_hour, end_hour, end_day_offset) ------------
_WIN = {
    "morning": (6, 12, 0),
    "afternoon": (12, 18, 0),
    "evening": (18, 21, 0),
    "night": (21, 6, 1),
}

_MID = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)


def _daypart(base_day, part):
    """Independent oracle: (start, end) AstroDates for a daypart on a given
    civil-day midnight ``base_day``."""
    sh, eh, eoff = _WIN[part]
    s = base_day.replace(hour=sh)
    e = (base_day + timedelta(days=eoff)).replace(hour=eh)
    return ad(s), ad(e)


def _weekday_base(target_idx):
    """Midnight of the next strictly-future weekday from the anchor."""
    days = (target_idx - ANCHOR.weekday()) % 7
    if days == 0:
        days = 7
    return _MID + timedelta(days=days)


# -- deictic day + daypart: this / tomorrow / yesterday -------------------

@pytest.mark.parametrize("text,base_off,part", [
    ("this morning", 0, "morning"),
    ("this afternoon", 0, "afternoon"),
    ("this evening", 0, "evening"),
    ("tomorrow morning", 1, "morning"),
    ("tomorrow afternoon", 1, "afternoon"),
    ("tomorrow evening", 1, "evening"),
    ("tomorrow night", 1, "night"),
    ("yesterday morning", -1, "morning"),
    ("yesterday afternoon", -1, "afternoon"),
    ("yesterday evening", -1, "evening"),
])
def test_deictic_daypart(text, base_off, part):
    base = _MID + timedelta(days=base_off)
    s, e = _daypart(base, part)
    assert start_end(text) == (s, e)


# -- the two idiomatic night words: tonight / last night ------------------

def test_tonight():
    # tonight == this civil day's night window (21:00 -> tomorrow 06:00)
    assert start_end("tonight") == _daypart(_MID, "night")


def test_last_night():
    # last night == yesterday's night window: 06-26 21:00 -> 06-27 06:00
    assert start_end("last night") == _daypart(_MID - timedelta(days=1), "night")


# -- weekday + daypart (weekday rolls to its next future occurrence) ------

_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
       "friday": 4, "saturday": 5, "sunday": 6}


def _wd_cases():
    out = []
    for name, idx in _WD.items():
        for part in ("morning", "afternoon", "evening", "night"):
            out.append((f"{name} {part}", idx, part))
    return out


@pytest.mark.parametrize("text,idx,part", _wd_cases())
def test_weekday_daypart(text, idx, part):
    base = _weekday_base(idx)
    s, e = _daypart(base, part)
    assert start_end(text) == (s, e)
