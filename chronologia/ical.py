"""RFC 5545 iCalendar interoperability -- a zero-dependency reader and writer.

Turns a :class:`~chronologia.events.Event` (or a bare
:class:`~chronologia.astrodate.DateSpan` / :class:`~chronologia.recurrence.Recurrence`)
into a ``VCALENDAR``/``VEVENT`` text block, and reads that subset back.  The
goal is *interop*: the output is accepted by real calendar clients, and input
those clients produce (for the properties we model) reads back into an
:class:`Event`.

What is written -- the modelled subset
--------------------------------------
A single ``VEVENT`` inside a ``VCALENDAR`` carrying:

* ``DTSTART`` / ``DTEND`` from the event's span.  A **day-wide-or-wider** span
  (midnight-aligned, a whole number of days) is written in the ``VALUE=DATE``
  form (:rfc:`5545#section-3.3.4`), the all-day convention where ``DTEND`` is
  the exclusive day after -- exactly our half-open :class:`DateSpan`.  A
  **clocked** span (a time of day, or a sub-day width) is written as a floating
  ``DATE-TIME`` (:rfc:`5545#section-3.3.5`).
* ``RRULE`` from :meth:`Recurrence.to_string <chronologia.recurrence.Recurrence.to_string>`
  (:rfc:`5545#section-3.8.5.3` / :rfc:`5545#section-3.3.10`).  A **movable**
  :class:`~chronologia.recurrence.HolidayRecurrence` has no RFC 5545 rule, so
  serializing one raises -- the writer refuses to emit a lie.
* ``SUMMARY`` -- the event label, TEXT-escaped per :rfc:`5545#section-3.3.11`.
* ``UID`` -- a **deterministic** content hash (:rfc:`5545#section-3.8.4.7`
  requires a UID; making it a hash of the content keeps re-serialization
  stable and free of wall-clock/random noise).

Line handling follows :rfc:`5545#section-3.1`: properties are emitted as
``NAME:VALUE`` content lines, CRLF-terminated, and folded to <=75 octets by
inserting ``CRLF`` + a space (never splitting a multi-byte UTF-8 sequence).

What is read
------------
:func:`from_ical` parses the properties above out of a ``VEVENT``, unfolding
lines first, ignoring any property it does not model (leniently -- a real
calendar file carries dozens), and raising :class:`ValueError` on structurally
broken input (no ``VEVENT``, no ``DTSTART``, an unparhseable value).
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from chronologia.astrodate import AstroDate, DateSpan
from chronologia.events import Event
from chronologia.recurrence import (HolidayRecurrence, Recurrence,
                                    parse_rrule)

__all__ = ["to_ical", "from_ical"]

_CRLF = "\r\n"
#: Fixed seed for a *bare* recurrence's DTSTART, so ``to_ical(recurrence)`` is
#: deterministic (anchor-free): the rule's first occurrence from the Unix epoch.
_ICAL_EPOCH = datetime(1970, 1, 1)
_PRODID = "-//chronologia//iCal//EN"


# --------------------------------------------------------------------------
# Writer.
# --------------------------------------------------------------------------
def _escape_text(value: str) -> str:
    """TEXT-value escaping (:rfc:`5545#section-3.3.11`): backslash, semicolon,
    comma and newline."""
    return (value.replace("\\", "\\\\")
                 .replace("\n", "\\n")
                 .replace(";", "\\;")
                 .replace(",", "\\,"))


def _fold(line: str) -> str:
    """Fold one content line to <=75 octets (:rfc:`5545#section-3.1`).

    Folding is on octet boundaries, but never inside a multi-byte UTF-8
    character; a continuation line begins with a single space.
    """
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    chunks = []
    start = 0
    limit = 75
    while start < len(raw):
        end = min(start + limit, len(raw))
        # back off so we do not split a multi-byte sequence
        while end < len(raw) and (raw[end] & 0xC0) == 0x80:
            end -= 1
        chunks.append(raw[start:end].decode("utf-8"))
        start = end
        limit = 74  # continuation lines carry a leading space (1 octet)
    return (_CRLF + " ").join(chunks)


def _check_ical_year(a: AstroDate) -> None:
    """RFC 5545 DATE/DATE-TIME is exactly four unsigned digits -- years
    0001..9999.  AstroDate is proleptic and unbounded, so a BC year (which would
    emit an invalid leading '-') or a >=10000 year (five digits) has NO valid
    iCal form; raise a clear error rather than emit malformed text that no
    calendar client -- including our own reader -- can parse back."""
    if not 1 <= a.year <= 9999:
        raise ValueError(
            f"iCal (RFC 5545) dates are limited to years 0001-9999; cannot "
            f"serialize year {a.year}")


def _fmt_date(a: AstroDate) -> str:
    # All-day (VALUE=DATE) events are floating by RFC 5545: they carry no time
    # and no zone.  A tz-aware all-day span's offset is therefore dropped -- and
    # deliberately NOT normalised to UTC the way a timed instant is, since a UTC
    # shift could move the whole day (2024-03-01 00:00+05:00 is still the
    # "1 March" all-day event, not 29 February).  The calendar day is preserved.
    _check_ical_year(a)
    return f"{a.year:04d}{a.month:02d}{a.day:02d}"


def _fmt_datetime(a: AstroDate) -> str:
    # A tz-aware instant must NOT be written as a floating local time (RFC 5545
    # §3.3.5): that silently re-reads as a different wall clock in every other
    # zone.  Normalise any offset to UTC and emit the trailing "Z"; a naive
    # AstroDate stays floating (no suffix), as before.
    zulu = ""
    if a.tzinfo is not None:
        a = a.astimezone(timezone.utc)
        zulu = "Z"
    _check_ical_year(a)   # the UTC shift can cross a year boundary
    return (f"{a.year:04d}{a.month:02d}{a.day:02d}"
            f"T{a.hour:02d}{a.minute:02d}{a.second:02d}{zulu}")


def _is_all_day(span: DateSpan) -> bool:
    """True when the span is midnight-aligned and a whole number of days --
    the all-day (``VALUE=DATE``) case."""
    s, e = span.start, span.end
    if (s.hour, s.minute, s.second, s.microsecond) != (0, 0, 0, 0):
        return False
    if (e.hour, e.minute, e.second, e.microsecond) != (0, 0, 0, 0):
        return False
    return (e - s) >= timedelta(days=1)


def _dt_lines(span: DateSpan) -> list:
    if _is_all_day(span):
        return [f"DTSTART;VALUE=DATE:{_fmt_date(span.start)}",
                f"DTEND;VALUE=DATE:{_fmt_date(span.end)}"]
    return [f"DTSTART:{_fmt_datetime(span.start)}",
            f"DTEND:{_fmt_datetime(span.end)}"]


def _normalise(obj: Union[Event, DateSpan, Recurrence, HolidayRecurrence]
               ) -> Event:
    """Coerce the writer's argument into an :class:`Event`."""
    if isinstance(obj, Event):
        return obj
    if isinstance(obj, DateSpan):
        return Event(summary="", span=obj)
    if isinstance(obj, (Recurrence, HolidayRecurrence)):
        from chronologia.events import first_occurrence
        span = first_occurrence(obj, _ICAL_EPOCH)
        if span is None:
            raise ValueError(
                "cannot serialize a recurrence that yields no occurrence near "
                "the iCal epoch seed")
        return Event(summary="", span=span, recurrence=obj)
    raise TypeError(
        f"to_ical expects an Event, DateSpan or Recurrence, got "
        f"{type(obj).__name__}")


def _uid(summary: str, dt_lines: list, rrule: Optional[str]) -> str:
    """A deterministic UID: a content hash, so the same event always serializes
    to the same identifier (:rfc:`5545#section-3.8.4.7`)."""
    payload = "\n".join([summary, *dt_lines, rrule or ""])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return f"{digest}@chronologia"


def to_ical(obj: Union[Event, DateSpan, Recurrence, HolidayRecurrence]) -> str:
    """Serialize ``obj`` to a ``VCALENDAR``/``VEVENT`` text block.

    ``obj`` may be an :class:`~chronologia.events.Event`, a bare
    :class:`~chronologia.astrodate.DateSpan` (an event with no summary or rule),
    or a :class:`~chronologia.recurrence.Recurrence` (whose ``DTSTART`` is seeded
    deterministically from the Unix epoch -- see the module docstring).

    Raises :class:`ValueError` when the event's recurrence is a movable
    :class:`~chronologia.recurrence.HolidayRecurrence` (no RFC 5545 rule can
    express it).
    """
    event = _normalise(obj)
    dt_lines = _dt_lines(event.span)

    rrule = None
    if event.recurrence is not None:
        # HolidayRecurrence.to_string() raises for movable feasts -- propagate.
        rrule = event.recurrence.to_string()
        # RFC 5545 3.3.10: UNTIL MUST share DTSTART's value type.  For an
        # all-day (VALUE=DATE) event the RRULE's canonical UNTIL still carries
        # the midnight time suffix (the recurrence string form always does);
        # drop it here so the emitted UNTIL is a bare DATE, matching DTSTART.
        if _is_all_day(event.span):
            rrule = re.sub(r"(UNTIL=\d{8})T\d{6}Z?", r"\1", rrule)

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{_PRODID}",
             "BEGIN:VEVENT",
             f"UID:{_uid(event.summary, dt_lines, rrule)}",
             *dt_lines]
    if rrule is not None:
        lines.append(f"RRULE:{rrule}")
    if event.summary:
        lines.append(f"SUMMARY:{_escape_text(event.summary)}")
    lines += ["END:VEVENT", "END:VCALENDAR"]
    return _CRLF.join(_fold(line) for line in lines) + _CRLF


# --------------------------------------------------------------------------
# Reader.
# --------------------------------------------------------------------------
def _unescape_text(value: str) -> str:
    out = []
    i = 0
    while i < len(value):
        ch = value[i]
        if ch == "\\" and i + 1 < len(value):
            nxt = value[i + 1]
            out.append({"n": "\n", "N": "\n"}.get(nxt, nxt))
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _unfold(text: str) -> list:
    """Undo RFC 5545 line folding: a line beginning with a space or tab is a
    continuation of the previous one."""
    physical = text.replace(_CRLF, "\n").replace("\r", "\n").split("\n")
    logical = []
    for line in physical:
        if line[:1] in (" ", "\t") and logical:
            logical[-1] += line[1:]
        else:
            logical.append(line)
    return [ln for ln in logical if ln != ""]


def _parse_ical_value(value: str, is_date: bool) -> AstroDate:
    """Parse a ``DATE`` (``YYYYMMDD``) or ``DATE-TIME`` (``YYYYMMDDTHHMMSS`` with
    an optional trailing ``Z``) into an :class:`AstroDate` (naive/floating)."""
    raw = value.strip()
    is_utc = raw[-1:] in ("Z", "z")   # trailing Z marks a UTC DATE-TIME
    v = raw.rstrip("Zz")
    date_part, _, time_part = v.partition("T")
    if len(date_part) != 8 or not date_part.isdigit():
        raise ValueError(f"malformed iCal date: {value!r}")
    y, mo, d = int(date_part[:4]), int(date_part[4:6]), int(date_part[6:8])
    if is_date or not time_part:
        return AstroDate(y, mo, d)
    if len(time_part) != 6 or not time_part.isdigit():
        raise ValueError(f"malformed iCal time: {value!r}")
    return AstroDate(y, mo, d, int(time_part[:2]), int(time_part[2:4]),
                     int(time_part[4:6]),
                     tzinfo=timezone.utc if is_utc else None)


def _zoned(dt: AstroDate, tzid: Optional[str], is_date: bool) -> AstroDate:
    """Anchor a floating ``DATE-TIME`` to its ``TZID`` zone (RFC 5545 3.2.19).

    A ``DTSTART;TZID=America/New_York:...`` value parses as a naive wall clock;
    the ``TZID`` names the IANA zone it belongs to, which real producers (Google
    Calendar, Outlook) use far more than a bare ``Z`` UTC value.  Attach that
    zone so the reader does not silently return a floating time with the wrong
    offset.  A ``DATE`` (all-day, floating by RFC) and an already-UTC value
    (trailing ``Z``) are left untouched; an unknown zone stays floating rather
    than raising, keeping the parse lenient."""
    if tzid is None or is_date or dt.tzinfo is not None:
        return dt
    try:
        from zoneinfo import ZoneInfo
        zone = ZoneInfo(tzid)
    except Exception:
        return dt   # unknown zone: stay floating, never raise
    # route through the library's honest DST resolution so the attached zone is
    # always self-consistent with the instant: a unique wall time gets the real
    # IANA zone; an ambiguous fall-back time takes the LATER occurrence (matching
    # the daypart-anchoring convention); a spring-forward gap time (which never
    # existed) keeps zoneinfo's push-forward default -- a malformed but concrete
    # instant an Event can still carry.
    from chronologia.astrodate import resolve_wall_clock
    resolved = resolve_wall_clock(dt.year, dt.month, dt.day, dt.hour,
                                  dt.minute, zone)
    if isinstance(resolved, AstroDate):
        base = resolved
    elif isinstance(resolved, tuple):
        base = resolved[1]              # later of the two fall-back occurrences
    else:                              # NeverExisted (gap): concrete fallback
        base = dt.replace(tzinfo=zone)
    # resolve_wall_clock works to minute precision; carry the seconds back.
    return base.replace(second=dt.second, microsecond=dt.microsecond)


def _split_property(line: str):
    """``NAME;PARAM=..:VALUE`` -> ``(name, params, value)`` (params lowercased
    keys).  The value may itself contain ``:`` (an RRULE never does; a URL
    might) so only the first unquoted colon splits."""
    if ":" not in line:
        raise ValueError(f"malformed content line (no ':'): {line!r}")
    head, _, value = line.partition(":")
    parts = head.split(";")
    name = parts[0].upper()
    params = {}
    for p in parts[1:]:
        if "=" in p:
            k, _, val = p.partition("=")
            # a param value may be a DQUOTE-wrapped quoted-string (RFC 5545
            # 3.1: param-value = paramtext / quoted-string) -- strip the quotes
            # so a quoted TZID ("America/New_York") resolves to its zone instead
            # of being looked up verbatim (with the quotes) and silently
            # dropped to a floating time.
            if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
                val = val[1:-1]
            # keep the parameter VALUE's original case: an IANA TZID
            # ("America/New_York") is case-sensitive, so it must not be
            # upper-cased.  Callers that compare a value ("VALUE=DATE") upper-
            # case at the comparison site instead.
            params[k.lower()] = val
    return name, params, value


def from_ical(text: str) -> Event:
    """Parse a ``VEVENT`` (the subset :func:`to_ical` writes) into an
    :class:`~chronologia.events.Event`.

    Unknown properties are ignored; the parse is lenient about extra content a
    real calendar carries.  Raises :class:`ValueError` on structurally broken
    input: no ``VEVENT`` block, or a ``VEVENT`` with no ``DTSTART``.
    """
    lines = _unfold(text)
    in_event = False
    seen_event = False
    dtstart = dtend = None
    start_is_date = end_is_date = False
    rrule = None
    summary = ""
    for line in lines:
        name, params, value = _split_property(line)
        if name == "BEGIN" and value.upper() == "VEVENT":
            in_event = True
            seen_event = True
            continue
        if name == "END" and value.upper() == "VEVENT":
            in_event = False
            continue
        if not in_event:
            continue
        if name == "DTSTART":
            start_is_date = params.get("value", "").upper() == "DATE" \
                or "T" not in value
            dtstart = _zoned(_parse_ical_value(value, start_is_date),
                             params.get("tzid"), start_is_date)
        elif name == "DTEND":
            end_is_date = params.get("value", "").upper() == "DATE" \
                or "T" not in value
            dtend = _zoned(_parse_ical_value(value, end_is_date),
                           params.get("tzid"), end_is_date)
        elif name == "RRULE":
            rrule = parse_rrule(value)
        elif name == "SUMMARY":
            summary = _unescape_text(value)

    if not seen_event:
        raise ValueError("no VEVENT found in iCal text")
    if dtstart is None:
        raise ValueError("VEVENT is missing the required DTSTART")
    if dtend is None:
        # A DATE with no DTEND is one day; a DATE-TIME with none is zero width.
        dtend = dtstart + timedelta(days=1) if start_is_date else dtstart
    span = DateSpan(dtstart, dtend)
    return Event(summary=summary, span=span, duration=None, recurrence=rrule)
