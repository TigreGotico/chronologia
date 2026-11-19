# -*- coding: utf-8 -*-
"""A definite article, a day word and a day number name a date, not a length."""
from datetime import datetime, timedelta

import pytest

from chronologia import AstroDate
from chronologia.events import extract_event
from chronologia.extract import extract_duration, extract_timespan

_DATES = [
    ("pt", "no dia 5 de dezembro"),
    ("pt", "o dia 25 de dezembro às 15h"),
    ("pt", "no dia cinco de dezembro"),
    ("pt", "no dia primeiro de maio"),
    ("pt", "no dia 1 de maio"),
    ("pt", "no dia primeiro de junho"),
    ("es", "el día primero de mayo"),
    ("it", "il giorno primo maggio"),
    ("gl", "o día primeiro de maio"),
    ("ca", "el dia primer de maig"),
    ("en", "the day first of may"),
    ("es", "el día 5 de diciembre"),
    ("gl", "o día 5 de decembro"),
    ("ca", "el dia 5 de desembre"),
    ("fr", "le jour 5 décembre"),
    ("it", "il giorno 5 dicembre"),
    ("en", "the day 5 of december"),
]

_LENGTHS = [
    ("pt", "um dia", timedelta(days=1)),
    ("pt", "uma semana e um dia", timedelta(days=8)),
    ("pt", "durante um dia", timedelta(days=1)),
    ("en", "a day 2 hours and 5 minutes", timedelta(days=1, hours=2, minutes=5)),
    ("fr", "un jour, 2 heures et 5 minutes", timedelta(days=1, hours=2, minutes=5)),
    ("it", "un giorno, 2 ore e 5 minuti", timedelta(days=1, hours=2, minutes=5)),
    ("es", "dura un día", timedelta(days=1)),
    ("pt", "2 dias", timedelta(days=2)),
]


@pytest.mark.parametrize("lang,text", _DATES)
def test_definite_day_number_is_no_duration(lang, text):
    assert extract_duration(text, lang) is None


@pytest.mark.parametrize("lang,text,expected", _LENGTHS)
def test_day_length_stays_a_duration(lang, text, expected):
    got = extract_duration(text, lang)
    assert got is not None and got.duration == expected


_ANCHOR = datetime(2025, 6, 18, 10, 30)

_SUMMARIES = [
    ("pt", "reunião no dia 5 de dezembro", "reunião"),
    ("es", "reunión el día 5 de diciembre", "reunión"),
    ("ca", "reunió el dia 5 de desembre", "reunió"),
    ("it", "riunione il giorno 5 dicembre", "riunione"),
    ("it", "festa il giorno 24 dicembre", "festa"),
    ("it", "esame il giorno primo maggio", "esame"),
    ("gl", "reunión o día 5 de decembro", "reunión"),
    ("gl", "reunión o dia 5 de decembro", "reunión"),
]

_ISSUE = "https://github.com/TigreGotico/chronologia/issues/1218"

_UNLABELLED = [
    ("en", "meeting on the day 5 of december", "meeting"),
    ("fr", "réunion le jour 5 décembre", "réunion"),
    ("de", "Treffen am Tag 5 Mai", "treffen"),
    ("nl", "vergadering op de dag 5 december", "vergadering"),
]


@pytest.mark.parametrize("lang,text,summary", _SUMMARIES)
def test_day_label_stays_out_of_the_summary(lang, text, summary):
    assert extract_event(text, lang, _ANCHOR).summary == summary


@pytest.mark.xfail(strict=True, reason=_ISSUE)
@pytest.mark.parametrize("lang,text,summary", _UNLABELLED)
def test_unlabelled_day_word_stays_out_of_the_summary(lang, text, summary):
    assert extract_event(text, lang, _ANCHOR).summary == summary



_RANGE_ANCHOR = datetime(2026, 1, 30, 10, 0)

_RANGES = [
    ("es", "desde el día 3 hasta el día 5 de marzo"),
    ("gl", "desde o día 3 ata o día 5 de marzo"),
    ("es", "entre el día 3 y el día 5 de marzo"),
    ("gl", "entre o día 3 e o día 5 de marzo"),
    ("ca", "entre el dia 3 i el dia 5 de març"),
    ("pt", "desde o dia 3 até o dia 5 de março"),
    ("it", "tra il giorno 3 e il giorno 5 marzo"),
]
_RANGE_END = datetime(2026, 3, 5) + timedelta(days=1)
_RANGE_GOLD = (AstroDate(2026, 3, 3), AstroDate.from_datetime(_RANGE_END))


@pytest.mark.parametrize("lang,text", _RANGES)
def test_day_range_event_span(lang, text):
    span = extract_event(text, lang, _RANGE_ANCHOR).span
    assert (span.start, span.end) == _RANGE_GOLD


@pytest.mark.parametrize("lang,text", _RANGES)
def test_day_range_timespan(lang, text):
    got = extract_timespan(text, lang, _RANGE_ANCHOR)
    assert (got.span.start, got.span.end) == _RANGE_GOLD
    assert got.remainder == ""


_PARTNERS = [
    (
        "pt",
        "desde o dia 10 até às 18h",
        datetime(2026, 2, 10),
        datetime(2026, 2, 10, 18) + timedelta(minutes=1),
    ),
    (
        "pt",
        "desde o dia 3 até daqui a 5 dias",
        datetime(2026, 2, 3),
        _RANGE_ANCHOR + timedelta(days=5) + timedelta(days=1),
    ),
    (
        "es",
        "desde las 10 hasta el día 5 de marzo",
        datetime(2026, 3, 5, 10),
        datetime(2026, 3, 5) + timedelta(days=1),
    ),
]


@pytest.mark.parametrize("lang,text,start,end", _PARTNERS)
def test_labelled_day_keeps_its_own_month_against_a_clock_or_offset(
        lang, text, start, end):
    got = extract_timespan(text, lang, _RANGE_ANCHOR)
    assert (got.span.start, got.span.end) == (
        AstroDate.from_datetime(start), AstroDate.from_datetime(end))
    assert got.remainder == ""
