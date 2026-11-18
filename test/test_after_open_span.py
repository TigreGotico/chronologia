"""A bare "after X" is the open span from the end of the next X onward.

The span has a start and no end. The gold is calendar arithmetic from the
anchor, Saturday 17 October 2026 12:00: the next Monday is 19 October, so
"after monday" starts at 00:00 on 20 October. The next 4 July and the next
13 May are in 2027.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, DateSpan, extract_candidates, extract_timespan
from chronologia.events import extract_event

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("lang, text, start", [
    ("en", "after monday", datetime(2026, 10, 20)),
    ("en", "after tomorrow", datetime(2026, 10, 19)),
    ("en", "after july 4th", datetime(2027, 7, 5)),
    ("en", "after july fourth", datetime(2027, 7, 5)),
    ("pt", "depois de segunda", datetime(2026, 10, 20)),
    ("de", "nach Montag", datetime(2026, 10, 20)),
])
def test_after_x_starts_where_x_ends_and_has_no_end(lang, text, start):
    span, rest = extract_timespan(text, lang, ANCHOR)
    assert span.open_end is True
    assert span.start == span.end == AstroDate.from_datetime(start)
    assert rest == ""


@pytest.mark.parametrize("lang, text, start", [
    ("en", "after monday", datetime(2026, 10, 20)),
    ("en", "after july 4th", datetime(2027, 7, 5)),
    ("fr", "après le 13 mai", datetime(2027, 5, 14)),
    ("de", "nach Montag", datetime(2026, 10, 20)),
])
def test_the_first_candidate_is_the_open_span(lang, text, start):
    first = extract_candidates(text, lang, ANCHOR, limit=3)[0]
    assert (first.span.start, first.span.open_end) == (
        AstroDate.from_datetime(start), True)
    assert first.remainder == ""


@pytest.mark.parametrize("text, start, end", [
    # an offset from christmas (25 December 2026), not an event length; the
    # offset arithmetic itself is the one origin/dev gives
    ("15 minutes after christmas", datetime(2026, 12, 26), datetime(2026, 12, 27)),
    ("the day after christmas", datetime(2026, 12, 26), datetime(2026, 12, 27)),
    ("the week after easter", datetime(2027, 3, 29), datetime(2027, 4, 5)),
])
def test_a_length_before_after_x_stays_an_offset_in_an_event(text, start, end):
    event = extract_event(text, "en", anchor=ANCHOR)
    assert event.duration is None
    assert (event.span.start, event.span.end) == (AstroDate.from_datetime(start),
                                                  AstroDate.from_datetime(end))


def test_before_x_stays_closed():
    span, _ = extract_timespan("before monday", "en", ANCHOR)
    assert span.open_end is False


def _point(*args):
    return AstroDate.from_datetime(datetime(*args))


def _open():
    return DateSpan(_point(2026, 10, 20), _point(2026, 10, 20), open_end=True)


def _month(month):
    return DateSpan(_point(2026, month, 1), _point(2026, month + 1, 1))


def test_an_open_span_stores_its_start_as_its_end():
    with pytest.raises(ValueError):
        DateSpan(_point(2026, 10, 20), _point(2026, 10, 21), open_end=True)


def test_an_open_span_contains_every_later_point():
    assert _open().contains(_point(2300, 1, 1))
    assert not _open().contains(_point(2026, 10, 19, 23, 59))


def test_set_operations_read_the_end_as_unbounded():
    after, october, september = _open(), _month(10), _month(9)
    assert after.overlaps(october) and october.overlaps(after)
    assert not after.overlaps(september)
    assert after.intersect(october) == DateSpan(_point(2026, 10, 20), _point(2026, 11, 1))
    assert after.intersect(september) is None
    assert after.union(october) == DateSpan(_point(2026, 10, 1), _point(2026, 10, 1),
                                            open_end=True)
    assert september.gap(after) == DateSpan(_point(2026, 10, 1), _point(2026, 10, 20))
    assert after.gap(september) == DateSpan(_point(2026, 10, 1), _point(2026, 10, 20))
    with pytest.raises(ValueError):
        after.union(september)


def test_an_open_span_round_trips_through_json_and_reads_as_open():
    assert DateSpan.from_json(_open().to_json()) == _open()
    assert "open_end" not in _month(10).to_json()
    assert str(_open()) == "2026-10-20 00:00 – .."
