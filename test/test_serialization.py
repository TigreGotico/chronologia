"""Round-trip laws for the JSON envelope convention (``to_json``/``from_json``).

Every public value type serializes to a ``json.dumps``-ready dict carrying a
``{"type": ...}`` envelope and rebuilds from it byte-for-value identically —
including deep-time years and timezone-aware instants.
"""
import json
from datetime import timedelta, timezone

import pytest

import chronologia as c
from chronologia import AstroDate, DateSpan, from_json, to_json
from chronologia.mars import DarianDate, MarsDate


def _roundtrip(value):
    """to_json -> json.dumps -> json.loads -> from_json must equal the input."""
    envelope = to_json(value)
    assert isinstance(envelope, dict)
    assert "type" in envelope
    revived = from_json(json.loads(json.dumps(envelope)))
    assert revived == value
    assert type(revived) is type(value)
    return envelope


# -- AstroDate --------------------------------------------------------------
@pytest.mark.parametrize("astro", [
    AstroDate(2024, 6, 1),
    AstroDate(2024, 6, 1, 13, 45, 30, 123456),
    AstroDate(1, 1, 1),
    AstroDate(0, 12, 31),                       # 1 BC
    AstroDate(-3760, 9, 7),                      # deep past (Anno Mundi epoch)
    AstroDate(12000, 6, 15),                     # far future, > 9999
    AstroDate(-45000, 3, 15),                    # tens of millennia BC
    AstroDate(2024, 3, 10, 2, 30, tzinfo=timezone.utc),
    AstroDate(2024, 3, 10, 2, 30,
              tzinfo=timezone(timedelta(hours=-4, minutes=-30))),
    AstroDate(-8000, 1, 1, 6, 0,
              tzinfo=timezone(timedelta(hours=5, minutes=45))),  # aware + deep
])
def test_astrodate_roundtrip(astro):
    env = _roundtrip(astro)
    assert env["type"] == "AstroDate"


def test_astrodate_from_json_rejects_wrong_type():
    with pytest.raises(ValueError):
        AstroDate.from_json({"type": "DateSpan", "iso": "2024-01-01T00:00:00"})


# -- DateSpan ---------------------------------------------------------------
@pytest.mark.parametrize("span", [
    DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 2, 1)),
    DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 1, 1)),      # point
    DateSpan(AstroDate(-500, 1, 1), AstroDate(500, 1, 1), "reconstructed"),
    DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 6, 1), "tabulated"),
    DateSpan(AstroDate(2020, 3, 29, 1, 0, tzinfo=timezone.utc),
             AstroDate(2020, 3, 29, 3, 0, tzinfo=timezone.utc)),
])
def test_datespan_roundtrip(span):
    env = _roundtrip(span)
    assert env["type"] == "DateSpan"
    assert env["basis"] == span.basis


def test_datespan_envelope_nests_astrodate():
    span = DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 2, 1))
    env = to_json(span)
    assert env["start"]["type"] == "AstroDate"
    assert env["end"]["type"] == "AstroDate"


# -- CalendarDate -----------------------------------------------------------
@pytest.mark.parametrize("key", ["hebrew", "julian", "coptic", "islamic_civil"])
def test_calendardate_roundtrip(key):
    cd = AstroDate(2024, 6, 1).to_calendar(key)
    env = _roundtrip(cd)
    assert env["type"] == "CalendarDate"
    assert env["calendar"] == key


# -- EdtfDate ---------------------------------------------------------------
@pytest.mark.parametrize("text", ["1984", "1984?", "1984~", "1984%",
                                   "1984-06", "1985-04-12", "1984/1989",
                                   "2004-06-11%"])
def test_edtfdate_roundtrip(text):
    ed = c.parse_edtf(text)
    env = _roundtrip(ed)
    assert env["type"] == "EdtfDate"


def test_edtfdate_open_flags_survive():
    ed = c.parse_edtf("1984/..")
    revived = from_json(to_json(ed))
    assert revived.open_end == ed.open_end
    assert revived.open_start == ed.open_start


# -- NamedPeriod ------------------------------------------------------------
def test_namedperiod_roundtrip_all():
    for period in c.PERIODS.values():
        _roundtrip(period)


def test_namedperiod_deep_time():
    # A deep-time geological period (millions of years) still round-trips.
    deep = [p for p in c.PERIODS.values() if p.span.start.year < -100000]
    assert deep, "expected some deep-time periods in the registry"
    for period in deep:
        _roundtrip(period)


# -- CivilHoliday -----------------------------------------------------------
@pytest.mark.parametrize("juris,year", [("PT", 2024), ("US", 2024),
                                        ("PT", 2020)])
def test_civilholiday_roundtrip(juris, year):
    for holiday in c.holidays_for(juris, year):
        env = _roundtrip(holiday)
        assert env["type"] == "CivilHoliday"
        assert isinstance(env["categories"], list)   # frozenset -> sorted list


# -- Recurrence -------------------------------------------------------------
@pytest.mark.parametrize("rrule", [
    "FREQ=DAILY",
    "FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=2",
    "FREQ=MONTHLY;BYDAY=-1FR",
    "FREQ=YEARLY;BYMONTH=9;BYDAY=1MO",
    "FREQ=YEARLY;COUNT=5",
    "FREQ=DAILY;UNTIL=20301231",
])
def test_recurrence_roundtrip(rrule):
    rec = c.parse_rrule(rrule)
    env = _roundtrip(rec)
    assert env["type"] == "Recurrence"
    assert env["rrule"] == rec.to_string()


# -- MarsDate / DarianDate --------------------------------------------------
@pytest.mark.parametrize("md", [
    MarsDate(0),
    MarsDate(50000, 12, 34, 56, 789012),
    MarsDate(-1000, 23, 59, 59, 999999),
])
def test_marsdate_roundtrip(md):
    env = _roundtrip(md)
    assert env["type"] == "MarsDate"


@pytest.mark.parametrize("dd", [
    DarianDate(1, 1, 1),
    DarianDate(200, 5, 10),
    DarianDate(-50, 24, 27),
])
def test_dariandate_roundtrip(dd):
    env = _roundtrip(dd)
    assert env["type"] == "DarianDate"


# -- dispatcher edge cases --------------------------------------------------
def test_from_json_rejects_non_envelope():
    with pytest.raises(ValueError):
        from_json({"no": "type"})
    with pytest.raises(ValueError):
        from_json("nonsense")


def test_from_json_rejects_unknown_type():
    with pytest.raises(ValueError):
        from_json({"type": "Nonexistent"})


def test_to_json_rejects_plain_object():
    with pytest.raises(TypeError):
        to_json(object())


def test_heterogeneous_list_roundtrip():
    values = [
        AstroDate(-3760, 9, 7),
        DateSpan(AstroDate(2020, 1, 1), AstroDate(2020, 2, 1)),
        c.parse_rrule("FREQ=WEEKLY"),
        MarsDate(50000),
    ]
    blob = json.dumps([to_json(v) for v in values])
    back = [from_json(d) for d in json.loads(blob)]
    assert back == values


# -- Recurrence clock pin + HolidayRecurrence -------------------------------
@pytest.mark.parametrize("rrule", [
    "FREQ=DAILY;BYHOUR=9",
    "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30",
])
def test_recurrence_clockpin_roundtrip(rrule):
    rec = c.parse_rrule(rrule)
    env = _roundtrip(rec)
    assert env["type"] == "Recurrence"
    assert env["rrule"] == rec.to_string()


def test_holiday_recurrence_roundtrip():
    from chronologia.recurrence import HolidayRecurrence
    hr = HolidayRecurrence("easter")
    env = _roundtrip(hr)
    assert env["type"] == "HolidayRecurrence"
    assert env["holiday"] == "easter"
    assert c.from_json(env) == hr
