"""nn: broad gold-verified sweeps -- full dates, month/year, seasons,
quarters, half-periods, relative offsets, clock, ISO weeks.

Every expected value is derived by independent date arithmetic (datetime /
dateutil / isocalendar), never read back from the engine.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, parse, start_end, span, ad, AstroDate

MONTHS = {1: 'januar', 2: 'februar', 3: 'mars', 4: 'april', 5: 'mai',
          6: 'juni', 7: 'juli', 8: 'august', 9: 'september', 10: 'oktober',
          11: 'november', 12: 'desember'}


def AD(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


# ---- full dates: <d>. <month> <year> -> one calendar day ----------------
import calendar as _cal  # noqa: E402

FULL = []
for _y in (1900, 1950, 1999, 2000, 2012, 2020, 2024):
    for _m in range(1, 13):
        for _d in (1, 15, _cal.monthrange(_y, _m)[1]):
            FULL.append((f"{_d}. {MONTHS[_m]} {_y}", _y, _m, _d))


@pytest.mark.parametrize("text,y,m,d", FULL)
def test_full_date(text, y, m, d):
    s = span(text)
    assert s.start == AstroDate(y, m, d)
    assert s.width == timedelta(days=1)


# ---- bare month + year --------------------------------------------------
MY = []
for _y in (1999, 2005, 2010, 2018, 2020, 2023):
    for _m in range(1, 13):
        MY.append((f"{MONTHS[_m]} {_y}", _y, _m))


@pytest.mark.parametrize("text,y,m", MY)
def test_month_year(text, y, m):
    s = datetime(y, m, 1)
    e = s + relativedelta(months=1)
    assert start_end(text) == (AD(s), AD(e))


# ---- seasons of a year (northern hemisphere, meteorological) -----------
SEASON = []
_SE = {'vår': (3, 6), 'sommar': (6, 9), 'haust': (9, 12)}
for _y in (2018, 2019, 2020, 2021, 2022):
    for _name, (_a, _b) in _SE.items():
        SEASON.append((f"{_name} {_y}", AstroDate(_y, _a, 1), AstroDate(_y, _b, 1)))
    SEASON.append((f"vinter {_y}", AstroDate(_y, 12, 1), AstroDate(_y + 1, 3, 1)))


@pytest.mark.parametrize("text,s,e", SEASON)
def test_season_of_year(text, s, e):
    assert start_end(text) == (s, e)


# ---- quarters (word + q-digit forms) -----------------------------------
QUARTER = []
_QO = {'fyrste': 1, 'andre': 2, 'tredje': 3, 'fjerde': 4}
for _y in (2018, 2019, 2020, 2021, 2022):
    for _name, _q in _QO.items():
        _sm = (_q - 1) * 3 + 1
        _s = datetime(_y, _sm, 1)
        _e = _s + relativedelta(months=3)
        QUARTER.append((f"{_name} kvartal {_y}", AD(_s), AD(_e)))
        QUARTER.append((f"q{_q} {_y}", AD(_s), AD(_e)))


@pytest.mark.parametrize("text,s,e", QUARTER)
def test_quarter(text, s, e):
    assert start_end(text) == (s, e)


# ---- half-periods of a year --------------------------------------------
HALF = []
for _y in (1999, 2005, 2018, 2020, 2023):
    HALF.append((f"fyrste halvdel av {_y}", AstroDate(_y, 1, 1), AstroDate(_y, 7, 1)))
    HALF.append((f"andre halvdel av {_y}", AstroDate(_y, 7, 1), AstroDate(_y + 1, 1, 1)))


@pytest.mark.parametrize("text,s,e", HALF)
def test_half_period(text, s, e):
    assert start_end(text) == (s, e)


# ---- relative numeric offsets ------------------------------------------
_PL = {'dag': 'dagar', 'veke': 'veker', 'år': 'år', 'time': 'timar',
       'månad': 'månader'}
_RU = {'dag': relativedelta(days=1), 'veke': relativedelta(weeks=1),
       'år': relativedelta(years=1), 'time': relativedelta(hours=1),
       'månad': relativedelta(months=1)}
PAST = []
FUT = []
for _u in ('dag', 'veke', 'år', 'time', 'månad'):
    for _n in (2, 3, 4, 5, 7, 10):
        PAST.append((f"for {_n} {_PL[_u]} sidan", _u, _n))
        FUT.append((f"om {_n} {_PL[_u]}", _u, _n))


@pytest.mark.parametrize("text,u,n", PAST)
def test_relative_past(text, u, n):
    d = _RU[u]
    assert start_end(text) == (AD(ANCHOR - n * d), AD(ANCHOR - (n - 1) * d))


@pytest.mark.parametrize("text,u,n", FUT)
def test_relative_future(text, u, n):
    d = _RU[u]
    assert start_end(text) == (AD(ANCHOR + n * d), AD(ANCHOR + (n + 1) * d))


# ---- clock: halv / kvart / digit ---------------------------------------
_HW = {1: 'ein', 2: 'to', 3: 'tre', 4: 'fire', 5: 'fem', 6: 'seks', 7: 'sju',
       8: 'åtte', 9: 'ni', 10: 'ti', 11: 'elleve', 12: 'tolv'}


def _clk(h, mi):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return AD(dt)


HALV = [(f"halv {_HW[n]}", (n - 1) % 24, 30) for n in range(1, 13)]
KVART = []
for n in range(1, 13):
    KVART.append((f"kvart over {_HW[n]}", n % 24, 15))
    KVART.append((f"kvart på {_HW[n]}", (n - 1) % 24, 45))
DIGIT = [(f"{h:02d}:{mi:02d}", h, mi)
         for h in (0, 6, 9, 12, 15, 18, 23) for mi in (0, 15, 30, 45)]


@pytest.mark.parametrize("text,h,mi", HALV)
def test_clock_halv(text, h, mi):
    s = span(text)
    assert s.start == _clk(h, mi)
    assert s.width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h,mi", KVART)
def test_clock_kvart(text, h, mi):
    assert span(text).start == _clk(h, mi)


@pytest.mark.parametrize("text,h,mi", DIGIT)
def test_clock_digit(text, h, mi):
    s = span(text)
    assert s.start == _clk(h, mi)
    assert s.width == timedelta(minutes=1)


# ---- ISO weeks with explicit year --------------------------------------
import datetime as _dt  # noqa: E402

ISOW = []
for _y in (2018, 2019, 2020, 2021):
    for _w in (1, 10, 25, 40, 52):
        _mon = _dt.date.fromisocalendar(_y, _w, 1)
        _s = datetime(_mon.year, _mon.month, _mon.day)
        ISOW.append((f"veke {_w} {_y}", AD(_s), AD(_s + timedelta(days=7))))


@pytest.mark.parametrize("text,s,e", ISOW)
def test_iso_week(text, s, e):
    assert start_end(text) == (s, e)
