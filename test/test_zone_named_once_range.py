"""A zone named on one end of a range governs the whole range and never raises."""
from datetime import datetime, timedelta, timezone

import pytest

from chronologia import extract_candidates, extract_event, extract_timespan

_ANCHOR = datetime(2017, 6, 27, 13, 4)   # a Tuesday
_PLUS2 = timezone(timedelta(hours=2))


def _at(*fields):
    return datetime(*fields, tzinfo=_PLUS2)


# (text, language, start, end) -- the wall clock keeps its digits, the zone is attached
_CASES = [
    ("until 1pm utc+2", "en", _at(2017, 6, 27, 13, 4), _at(2017, 6, 28, 13, 1)),
    ("since 1pm utc+2", "en", _at(2017, 6, 27, 13, 0), _at(2017, 6, 27, 13, 4)),
    ("since 1pm utc+2 until friday", "en",
     _at(2017, 6, 27, 13, 0), _at(2017, 7, 1, 0, 0)),
    ("from 9am utc+2 to 5pm on monday", "en",
     _at(2017, 7, 3, 9, 0), _at(2017, 7, 3, 17, 1)),
    ("from tomorrow at 1pm utc+2 to friday", "en",
     _at(2017, 6, 30, 13, 0), _at(2017, 7, 1, 0, 0)),
    ("from 1pm to 3pm utc+2", "en", _at(2017, 6, 28, 13, 0), _at(2017, 6, 28, 15, 1)),
    ("bis 15:00 utc+2", "de", _at(2017, 6, 27, 13, 4), _at(2017, 6, 27, 15, 1)),
    ("jusqu'à 15h utc+2", "fr", _at(2017, 6, 27, 13, 4), _at(2017, 6, 27, 15, 1)),
    ("até às 15:00 utc+2", "pt", _at(2017, 6, 27, 13, 4), _at(2017, 6, 27, 15, 1)),
    ("desde las 13:00 utc+2", "es", _at(2017, 6, 27, 13, 0), _at(2017, 6, 27, 13, 4)),
]

@pytest.mark.parametrize("text,lang,start,end", _CASES)
def test_timespan_reads_the_zone_on_both_ends(text, lang, start, end):
    got = extract_timespan(text, lang, _ANCHOR)
    assert got is not None
    assert (got.span.start.datetime(), got.span.end.datetime()) == (start, end)


@pytest.mark.parametrize("text,lang,start,end", _CASES)
def test_top_candidate_is_the_timespan(text, lang, start, end):
    top = extract_candidates(text, lang, _ANCHOR)[0]
    assert (top.span.start.datetime(), top.span.end.datetime()) == (start, end)


@pytest.mark.parametrize("text,lang,start,end", _CASES)
def test_event_starts_at_the_range_start(text, lang, start, end):
    got = extract_event(text, lang, _ANCHOR)
    assert got is not None
    assert got.span.start.datetime() == start


def test_bare_before_with_a_zone_does_not_raise():
    assert extract_timespan("before 1pm utc+2", "en", _ANCHOR) is not None
    assert extract_event("before 1pm utc+2", "en", _ANCHOR) is not None


@pytest.mark.parametrize("zone", ["gmt", "utc", "est", "cet", "+0200", "-05:00"])
def test_closed_range_with_any_zone_does_not_raise(zone):
    for extract in (extract_timespan, extract_candidates, extract_event):
        assert extract(f"from 1pm to 3pm {zone}", "en", _ANCHOR)
