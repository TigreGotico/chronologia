"""Resolver stage: exact resolved spans against a fixed anchor
(datetime(2017, 6, 27, 13, 4), a Tuesday) for every implemented
construction, plus adversarial inputs that must never raise.

``Resolution.value`` is a DateSpan; its ``.start`` is the resolved instant
and its ``.resolution`` is derived from the span width."""
from datetime import datetime

import pytest
from engine_helpers import ANCHOR, load_zz, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.extract import Resolver
from chronologia.extract.model import Match
from chronologia.resolution import DateTimeResolution


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- relative_offset (sign comes from the marker's declared direction) -----

def test_relative_offset_future_days():
    r = _one("3 zdays zhence")
    assert r.value.start == AstroDate(2017, 6, 30, 13, 4)
    assert r.value.resolution == DateTimeResolution.DAY


def test_relative_offset_past_weeks():
    r = _one("zago 2 zweeks")
    assert r.value.start == AstroDate(2017, 6, 13, 13, 4)
    assert r.value.resolution == DateTimeResolution.WEEK


def test_relative_offset_future_months_prefix_marker():
    r = _one("zin 2 zmonths")
    assert r.value.start == AstroDate(2017, 8, 27, 13, 4)
    assert r.value.resolution == DateTimeResolution.MONTH


def test_relative_offset_past_year():
    r = _one("zago 1 zyear")
    assert r.value.start == AstroDate(2016, 6, 27, 13, 4)
    assert r.value.resolution == DateTimeResolution.YEAR


# -- named_day (midnight of the resolved day, day-wide) --------------------

@pytest.mark.parametrize("text,day", [
    ("ztoday", 27), ("zmorrow", 28), ("zyester", 26), ("zovermorrow", 29)])
def test_named_day(text, day):
    r = _one(text)
    assert r.value.start == AstroDate(2017, 6, day, 0, 0)
    assert r.value.resolution == DateTimeResolution.DAY


# -- weekday_ref -----------------------------------------------------------

def test_weekday_next():
    assert _one("znext zfri").value.start == AstroDate(2017, 6, 30)


def test_weekday_last():
    assert _one("zlast zmon").value.start == AstroDate(2017, 6, 26)


def test_weekday_this():
    assert _one("zthis zwed").value.start == AstroDate(2017, 6, 28)


# -- calendar_date, both slot orders ---------------------------------------

def test_calendar_mdy_full():
    r = _one("zjun 5 2027")
    assert r.value.start == AstroDate(2027, 6, 5)
    assert r.value.resolution == DateTimeResolution.DAY


def test_calendar_dmy_full():
    assert _one("5 zof zjun 2027").value.start == AstroDate(2027, 6, 5)


def test_calendar_month_and_bare_year_keeps_year():
    r = _one("zjun 2027")
    assert r.value.start == AstroDate(2027, 6, 1)
    # a bare month is month-wide: [june 2027, july 2027)
    assert r.value.end == AstroDate(2027, 7, 1)
    assert r.value.resolution == DateTimeResolution.MONTH


def test_calendar_month_only():
    r = _one("zjun")
    assert r.value.start == AstroDate(2017, 6, 1)
    assert r.value.end == AstroDate(2017, 7, 1)
    assert r.value.resolution == DateTimeResolution.MONTH


def test_calendar_prefer_future_bumps_past_day():
    # June 5 is before the anchor (June 27) -> prefer_future -> next year
    assert _one("zjun 5").value.start == AstroDate(2018, 6, 5)


def test_calendar_prefer_future_keeps_future_day():
    assert _one("zaug 5").value.start == AstroDate(2017, 8, 5)


# -- iso_date --------------------------------------------------------------

def test_iso_date():
    r = _one("2017-06-30")
    assert r.value.start == AstroDate(2017, 6, 30)
    assert r.value.resolution == DateTimeResolution.DAY


# -- adversarial: never raise, resolve to nothing --------------------------

@pytest.mark.parametrize("text", [
    "", "zzz garbage 999", "zago zweeks", "3 zdays", "zfeb 30", "zapr 31",
    "2017-13-40", "znext", "zof zof zof"])
def test_adversarial_never_raises(text):
    assert zz_engine().resolve(text, ANCHOR) == []


def test_impossible_iso_returns_none_directly():
    eng = zz_engine()
    toks = eng.tokenize("2017-02-30")
    m = Match("iso_date", (0, 1), {"ISO": toks[0]})
    assert Resolver(eng.spec).resolve(m, ANCHOR) is None


# -- declared-but-unimplemented constructions ------------------------------

@pytest.mark.parametrize("name", ["era_date"])
def test_unimplemented_constructions_raise(name):
    with pytest.raises(NotImplementedError):
        Resolver(load_zz()).resolve(Match(name, (0, 1), {}), ANCHOR)
