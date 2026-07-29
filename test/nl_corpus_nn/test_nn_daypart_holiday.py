"""nn: daypart windows on weekdays, and holidays (fixed + computus-derived).

Daypart windows exercised are the ones the nn locale actually resolves:
ettermiddag = 12:00-18:00, kveld = 18:00-24:00.  Holiday gold is fixed-date
or derived from independently-known Easter dates.

DIVERGENCE (not tested, flagged as gaps): ``om morgonen`` / ``om formiddagen``
do NOT resolve (no morning daypart window); ``jul`` mis-resolves to the month
of July rather than Christmas.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, parse, start_end, AstroDate


def AD(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


WD = {0: 'måndag', 1: 'tysdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag',
      5: 'laurdag', 6: 'sundag'}


def _next_wd(wd):
    d = ANCHOR.date()
    for i in range(1, 8):
        cand = d + timedelta(days=i)
        if cand.weekday() == wd:
            return cand


DAYPART = []
for _wd in range(7):
    _day = _next_wd(_wd)
    _base = datetime(_day.year, _day.month, _day.day)
    DAYPART.append((f"{WD[_wd]} ettermiddag",
                    _base + timedelta(hours=12), _base + timedelta(hours=18)))
    DAYPART.append((f"{WD[_wd]} kveld",
                    _base + timedelta(hours=18), _base + timedelta(hours=24)))


@pytest.mark.parametrize("text,s,e", DAYPART)
def test_weekday_daypart(text, s, e):
    assert start_end(text) == (AD(s), AD(e))


# ---- fixed-date holidays -----------------------------------------------
FIXED = []
for _y in (2018, 2019, 2020, 2021):
    FIXED.append((f"julaftan {_y}", datetime(_y, 12, 24)))
    FIXED.append((f"fyrste juledag {_y}", datetime(_y, 12, 25)))
    FIXED.append((f"andre juledag {_y}", datetime(_y, 12, 26)))
    FIXED.append((f"nyttårsaftan {_y}", datetime(_y, 12, 31)))


@pytest.mark.parametrize("text,d", FIXED)
def test_holiday_fixed(text, d):
    assert start_end(text) == (AD(d), AD(d + timedelta(days=1)))


# ---- computus-derived holidays (independently-known Easter Sundays) ----
_EASTER = {2018: datetime(2018, 4, 1), 2019: datetime(2019, 4, 21),
           2020: datetime(2020, 4, 12), 2021: datetime(2021, 4, 4)}
COMPUTUS = []
for _y, _es in _EASTER.items():
    COMPUTUS.append((f"langfredag {_y}", _es - timedelta(days=2)))
    COMPUTUS.append((f"kristi himmelfartsdag {_y}", _es + timedelta(days=39)))
    COMPUTUS.append((f"pinse {_y}", _es + timedelta(days=49)))


@pytest.mark.parametrize("text,d", COMPUTUS)
def test_holiday_computus(text, d):
    assert start_end(text) == (AD(d), AD(d + timedelta(days=1)))


# ---- "<decade>-talet" resolves to the full decade span ----
# "1990-talet" means the decade 1990-1999 (span 1990-01-01 .. 2000-01-01).
# The nn locale binds the "-talet" definite decade suffix to decade_ref.
@pytest.mark.parametrize("dec", [1920, 1950, 1980, 1990, 2000, 2010])
def test_decade_span(dec):
    assert start_end(f"{dec}-talet") == (AstroDate(dec, 1, 1),
                                         AstroDate(dec + 10, 1, 1))
