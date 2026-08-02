# -*- coding: utf-8 -*-
"""RFC 5545 iCalendar writer/reader: golds, round-trips and the movable guard.

Three guarantees:

* :func:`to_ical` output matches hand-written expected ``VEVENT`` blocks (the
  golds), so the exact wire text -- ``VALUE=DATE`` vs ``DATE-TIME``, the
  deterministic UID, the RRULE line -- is pinned.
* ``from_ical(to_ical(e)) == e`` on (summary, span, recurrence) for a battery
  of events extracted across five languages.
* a movable :class:`~chronologia.recurrence.HolidayRecurrence` event refuses to
  serialize (no RFC 5545 rule can express it).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate, DateSpan
from chronologia.events import Event, extract_event
from chronologia.ical import from_ical, to_ical
from chronologia.recurrence import HolidayRecurrence, parse_rrule

CRLF = "\r\n"
ANCHOR = datetime(2026, 7, 22, 12, 0)   # a Wednesday


def _key(ev):
    return (ev.summary, ev.span, ev.recurrence)


# -- golds: exact wire text -------------------------------------------------
_GOLD_TIMED_RECURRING = CRLF.join([
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//chronologia//iCal//EN",
    "BEGIN:VEVENT",
    "UID:72b81754e67442872d458e4d09c25ed2@chronologia",
    "DTSTART:20260722T090000",
    "DTEND:20260722T093000",
    "RRULE:FREQ=WEEKLY;BYDAY=WE;BYHOUR=9",
    "SUMMARY:my weekly meeting",
    "END:VEVENT",
    "END:VCALENDAR",
]) + CRLF

_GOLD_ALLDAY = CRLF.join([
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//chronologia//iCal//EN",
    "BEGIN:VEVENT",
    "UID:5f40e3835e86850ceb1efd6aea554410@chronologia",
    "DTSTART;VALUE=DATE:20261225",
    "DTEND;VALUE=DATE:20261226",
    "SUMMARY:my birthday party",
    "END:VEVENT",
    "END:VCALENDAR",
]) + CRLF

_GOLD_ALLDAY_RECURRING = CRLF.join([
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//chronologia//iCal//EN",
    "BEGIN:VEVENT",
    "UID:3a211e6f52d277b5301a000e361a5f28@chronologia",
    "DTSTART;VALUE=DATE:20261225",
    "DTEND;VALUE=DATE:20261226",
    "RRULE:FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25",
    "SUMMARY:christmas dinner",
    "END:VEVENT",
    "END:VCALENDAR",
]) + CRLF


@pytest.mark.parametrize("text,gold", [
    ("my weekly meeting every wednesday at 9 for 30 minutes",
     _GOLD_TIMED_RECURRING),
    ("my birthday party on december 25th", _GOLD_ALLDAY),
    ("christmas dinner every christmas", _GOLD_ALLDAY_RECURRING),
])
def test_to_ical_gold(text, gold):
    ev = extract_event(text, "en", anchor=ANCHOR)
    assert to_ical(ev) == gold


# -- round-trip battery across five languages -------------------------------
_ROUNDTRIP = [
    ("en", "my weekly meeting every wednesday at 9 for 30 minutes"),
    ("en", "call mom every sunday"),
    ("en", "my birthday party on december 25th"),
    ("pt", "minha reunião toda quarta às 9 por 30 minutos"),
    ("pt", "aniversário em 25 de dezembro"),
    ("es", "cena de navidad cada navidad"),
    ("es", "cita el viernes a las 15"),
    ("de", "sync jeden mittwoch um 9"),
    ("de", "geburtstag am 25. dezember"),
    ("fr", "dîner de noël chaque noël"),
    ("fr", "déjeuner le 5 juin"),
]


@pytest.mark.parametrize("lang,text", _ROUNDTRIP)
def test_ical_roundtrip(lang, text):
    ev = extract_event(text, lang, anchor=ANCHOR)
    assert ev is not None
    back = from_ical(to_ical(ev))
    assert _key(back) == _key(ev)


# -- writer also accepts a bare span and a bare recurrence ------------------
def test_to_ical_bare_span_roundtrip():
    span = DateSpan(AstroDate(2026, 6, 5, 15, 0), AstroDate(2026, 6, 5, 16, 0))
    back = from_ical(to_ical(span))
    assert back.span == span
    assert back.summary == ""
    assert back.recurrence is None


def test_to_ical_bare_recurrence_is_deterministic():
    rec = parse_rrule("FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25")
    first = to_ical(rec)
    assert to_ical(rec) == first          # deterministic (epoch-seeded)
    back = from_ical(first)
    assert back.recurrence == rec


# -- movable feast refuses to serialize -------------------------------------
def test_movable_holiday_event_ical_raises():
    ev = extract_event("yoga every easter", "en", anchor=ANCHOR)
    assert isinstance(ev.recurrence, HolidayRecurrence)
    with pytest.raises(ValueError):
        to_ical(ev)


def test_movable_holiday_recurrence_ical_raises():
    with pytest.raises(ValueError):
        to_ical(HolidayRecurrence("easter"))


# -- TEXT escaping and 75-octet line folding round-trip ---------------------
def test_summary_escaping_roundtrip():
    span = DateSpan(AstroDate(2026, 6, 5), AstroDate(2026, 6, 6))
    ev = Event(summary="dinner; with A, B \\ C", span=span)
    text = to_ical(ev)
    assert "SUMMARY:dinner\\; with A\\, B \\\\ C" in text
    assert from_ical(text).summary == ev.summary


def test_long_summary_folds_and_unfolds():
    span = DateSpan(AstroDate(2026, 6, 5), AstroDate(2026, 6, 6))
    summary = "a very long summary " * 6      # > 75 octets
    ev = Event(summary=summary.strip(), span=span)
    text = to_ical(ev)
    # every physical line stays within the 75-octet fold limit
    for line in text.split(CRLF):
        assert len(line.encode("utf-8")) <= 75
    assert from_ical(text).summary == summary.strip()


def test_from_ical_ignores_unknown_and_needs_vevent():
    with pytest.raises(ValueError):
        from_ical("BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")
    good = (
        "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\n"
        "DTSTART;VALUE=DATE:20260605\r\nDTEND;VALUE=DATE:20260606\r\n"
        "SUMMARY:picnic\r\nX-CUSTOM-PROP:ignored\r\n"
        "END:VEVENT\r\nEND:VCALENDAR\r\n")
    ev = from_ical(good)
    assert ev.summary == "picnic"
    assert ev.span == DateSpan(AstroDate(2026, 6, 5), AstroDate(2026, 6, 6))


def test_from_ical_quoted_tzid_param_resolves_zone():
    # A DQUOTE-wrapped param value is valid RFC 5545 (param-value =
    # paramtext / quoted-string).  A quoted TZID must be unquoted before the
    # zone lookup, otherwise ZoneInfo('"America/New_York"') fails and the time
    # silently falls back to floating (naive).  Regression: _split_property kept
    # the surrounding quotes.
    quoted = (
        "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\n"
        "DTSTART;TZID=\"America/New_York\":20260615T140000\r\n"
        "DTEND;TZID=\"America/New_York\":20260615T150000\r\n"
        "END:VEVENT\r\nEND:VCALENDAR\r\n")
    ev = from_ical(quoted)
    assert ev.span.start.tzinfo is not None
    assert str(ev.span.start.tzinfo) == "America/New_York"
    # unquoted TZID is unaffected
    unquoted = quoted.replace('"America/New_York"', "America/New_York")
    assert str(from_ical(unquoted).span.start.tzinfo) == "America/New_York"
