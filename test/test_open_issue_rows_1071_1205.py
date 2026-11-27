# -*- coding: utf-8 -*-
"""Open-issue rows, 1071 to 1205.

Each row asserts the value its issue expects.  The mark is a strict xfail that
carries the issue URL, so the run turns red when a fix lands and the fix removes
the mark.  Every expected value comes from the issue text or from arithmetic on
the anchor, never from this library.

Anchor: Tuesday 2017-06-27 13:04, unless a row names its own.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_candidates, extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
A = ANCHOR
dt = datetime
URL = "https://github.com/TigreGotico/chronologia/issues/{}"


class Within:
    """The start lies in [lo, hi)."""

    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi

    def matches(self, value):
        return self.lo <= value < self.hi

    def __repr__(self):
        return "Within({}, {})".format(self.lo, self.hi)


def _matches(expected, value):
    if isinstance(expected, Within):
        return expected.matches(value)
    if isinstance(expected, tuple):
        return value in expected
    if isinstance(expected, int):
        return value.year == expected
    if isinstance(expected, date) and not isinstance(expected, datetime):
        return value.date() == expected
    return value == expected


# Span rows that read right on dev: plain tests that keep the fix.
FIXED_SPANS = {
    "um 6 früh",
    "um sechs früh",
    "um 6:30 früh",
    "klokka 6:30 om morgenen",
    "klokka 6:30 om morgonen",
    "klokka 6 om morgenen",
    "klokka 6 om morgonen",
    "klokka 6 om kvelden",
    "klokka 6:30 om kvelden",
    "klokka 8 i kveld",
    "klokka 6 om ettermiddagen",
}


def _case(fixed, issue, *row):
    marks = () if row[1] in fixed else pytest.mark.xfail(raises=AssertionError,
        strict=True, reason=URL.format(issue))
    return pytest.param(
        *row, marks=marks, id="{}-{}-{}".format(issue, row[0], row[1]))


# issue, lang, text, expected start, expected end or None, expected remainder
# or None, anchor
SPANS = [

    (1071, "de", "um 6 früh", dt(2017, 6, 28, 6, 0), None, "", A),
    (1071, "de", "um sechs früh", dt(2017, 6, 28, 6, 0), None, "", A),
    (1071, "de", "um 6:30 früh", dt(2017, 6, 28, 6, 30), None, "", A),
    (1071, "nb", "klokka 6:30 om morgenen", dt(2017, 6, 28, 6, 30), None, "", A),
    (1071, "nn", "klokka 6:30 om morgonen", dt(2017, 6, 28, 6, 30), None, "", A),
    (1071, "nb", "klokka 6 om morgenen", dt(2017, 6, 28, 6, 0), None, "", A),
    (1071, "nn", "klokka 6 om morgonen", dt(2017, 6, 28, 6, 0), None, "", A),
    (1071, "nb", "klokka 6 om kvelden", dt(2017, 6, 27, 18, 0), None, "", A),
    (1071, "nb", "klokka 6:30 om kvelden", dt(2017, 6, 27, 18, 30), None, "", A),
    (1071, "nb", "klokka 8 i kveld", dt(2017, 6, 27, 20, 0), None, "", A),
    (1071, "nb", "klokka 6 om ettermiddagen", dt(2017, 6, 27, 18, 0), None, "", A),
    (1071, "nn", "klokka 6 om kvelden", dt(2017, 6, 27, 18, 0), None, "", A),
    (1071, "nn", "klokka 8 i kveld", dt(2017, 6, 27, 20, 0), None, "", A),
    (1087, "pt", "lembra-me uma hora antes do natal", dt(2026, 12, 24, 23, 0), None, "lembra-me", dt(2026, 9, 25, 12, 0)),
    (1087, "pt", "meia hora antes do ano novo", dt(2026, 12, 31, 23, 30), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "pt", "duas horas antes do natal", dt(2026, 12, 24, 22, 0), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "it", "ricordami un'ora prima di capodanno", dt(2026, 12, 31, 23, 0), None, "ricordami", dt(2026, 9, 25, 12, 0)),
    (1087, "es", "un cuarto de hora antes de navidad", dt(2026, 12, 24, 23, 45), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "es", "tres cuartos de hora antes de navidad", dt(2026, 12, 24, 23, 15), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "fr", "un quart d'heure avant noël", dt(2026, 12, 24, 23, 45), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "fr", "trois quarts d'heure avant noël", dt(2026, 12, 24, 23, 15), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "pt", "um quarto de hora antes do natal", dt(2026, 12, 24, 23, 45), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "pt", "três quartos de hora antes do natal", dt(2026, 12, 24, 23, 15), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "ca", "un quart d'hora abans de nadal", dt(2026, 12, 24, 23, 45), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "gl", "un cuarto de hora antes do nadal", dt(2026, 12, 24, 23, 45), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "en", "remind me an hour before new year", dt(2026, 12, 31, 23, 0), None, "remind me", dt(2026, 9, 25, 12, 0)),
    (1087, "en", "remind me half an hour before new year", dt(2026, 12, 31, 23, 30), None, "remind me", dt(2026, 9, 25, 12, 0)),
    (1087, "en", "an hour and a half before christmas", dt(2026, 12, 24, 22, 30), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "en", "the hour before christmas", dt(2026, 12, 24, 23, 0), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "en", "an hour before easter", dt(2027, 3, 27, 23, 0), None, "", dt(2026, 9, 25, 12, 0)),
    (1087, "sv", "en kvart före jul", dt(2026, 12, 24, 23, 45), None, "", dt(2026, 9, 25, 12, 0)),
    (1097, "fr", "avant noël", dt(2026, 9, 25, 12, 0), dt(2026, 12, 25, 0, 0), "", dt(2026, 9, 25, 12, 0)),
    (1097, "en", "before christmas", dt(2026, 9, 25, 12, 0), dt(2026, 12, 25, 0, 0), "", dt(2026, 9, 25, 12, 0)),
    (1097, "sv", "före jul", dt(2026, 9, 25, 12, 0), dt(2026, 12, 25, 0, 0), "", dt(2026, 9, 25, 12, 0)),
    (1103, "pt", "tarde", dt(2023, 1, 15, 12, 0), dt(2023, 1, 15, 19, 0), None, dt(2023, 1, 15, 12, 0)),
    (1103, "pt", "noite", dt(2023, 1, 15, 19, 0), dt(2023, 1, 16, 0, 0), None, dt(2023, 1, 15, 12, 0)),
    (1103, "it", "stasera", Within(dt(2017, 6, 27, 16, 0), dt(2017, 6, 27, 22, 0)), None, None, A),
    (1103, "it", "stasera alle 10", dt(2017, 6, 27, 22, 0), None, "", A),
    (1134, "nl", "vandaag 's avonds om 8:00", dt(2017, 6, 27, 20, 0), None, "", A),
    (1134, "nl", "vandaag 's avonds om 8:00", dt(2017, 6, 27, 20, 0), None, "", dt(2017, 6, 27, 5, 0)),
    (1134, "nl", "vandaag 's avonds om 8:00", dt(2017, 6, 27, 20, 0), None, "", dt(2017, 6, 27, 21, 0)),
    (1134, "nl", "vandaag 's avonds om 8 uur", dt(2017, 6, 27, 20, 0), None, "", dt(2017, 6, 27, 21, 0)),
    (1190, "pl", "w 2024 roku", dt(2024, 1, 1), None, "", A),
    (1190, "pl", "2024 rok", dt(2024, 1, 1), None, "", A),
    (1190, "pl", "15 października 2024 roku", dt(2024, 10, 15), None, "", A),
    (1190, "cs", "v roce 2024", dt(2024, 1, 1), None, "", A),
    (1190, "sk", "v roku 2024", dt(2024, 1, 1), None, "", A),
    (1190, "bg", "през 2024 година", dt(2024, 1, 1), None, "", A),
    (1190, "bg", "2024 година", dt(2024, 1, 1), None, "", A),
    (1190, "hr", "u 2024. godini", dt(2024, 1, 1), None, "", A),
    (1190, "hr", "2024. godine", dt(2024, 1, 1), None, "", A),
    (1191, "ro", "peste o jumătate de oră", dt(2026, 1, 30, 10, 30), None, None, dt(2026, 1, 30, 10, 0)),
    (1191, "ro", "peste o jumatate de ora", dt(2026, 1, 30, 10, 30), None, None, dt(2026, 1, 30, 10, 0)),
    (1191, "ro", "peste o jumătate de zi", dt(2026, 1, 30, 22, 0), None, None, dt(2026, 1, 30, 10, 0)),
    (1196, "pt", "às 9 uma hora antes do natal", dt(2026, 12, 24, 21, 0), None, "", dt(2026, 9, 25, 12, 0)),
    (1196, "en", "at 9 one hour before christmas", dt(2026, 12, 24, 21, 0), None, "", dt(2026, 9, 25, 12, 0)),
    (1197, "en", "a few hours before christmas", dt(2026, 9, 25, 12, 0), dt(2026, 12, 25, 0, 0), "", dt(2026, 9, 25, 12, 0)),
    (1197, "en", "several hours before christmas", dt(2026, 9, 25, 12, 0), dt(2026, 12, 25, 0, 0), "", dt(2026, 9, 25, 12, 0)),
    (1199, "es-es", "mañana a las 3 de la tarde compra las 3 cosas", dt(2026, 9, 26, 15, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1199, "es-es", "mañana a las 3 de la tarde dale las 3 llaves a juan", dt(2026, 9, 26, 15, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1199, "gl-es", "mañá ás 3 da tarde compra as 3 cousas", dt(2026, 9, 26, 15, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1199, "gl-es", "mañá ás 3 da tarde chama ás 5 veciñas", dt(2026, 9, 26, 15, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1199, "ca-es", "demà a les 3 de la tarda compra les 3 coses", dt(2026, 9, 26, 15, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1199, "es-es", "mañana a las 3 de la tarde compra las 5 cosas", dt(2026, 9, 26, 15, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1200, "an", "reunión manyana a las 5 de la tardi", dt(2017, 6, 28, 17, 0), None, "reunión", A),
    (1200, "an", "a las 9 d'o maitín", dt(2017, 6, 28, 9, 0), None, "", A),
    (1200, "an", "o 15 de chuliol de 2018 a las 9 d'o maitín", dt(2018, 7, 15, 9, 0), None, "", A),
    (1200, "es-ES", "a las 8 en la mañana", dt(2026, 10, 18, 8, 0), None, "", dt(2026, 10, 17, 12, 0)),
    (1200, "eu", "23:00 gauean", dt(2017, 6, 27, 23, 0), None, "", A),
    (1200, "eu", "3:00 gauean", dt(2017, 6, 28, 3, 0), None, "", A),
    (1200, "bg", "следващата сряда по обед", dt(2017, 7, 5, 12, 0), None, "", dt(2017, 6, 28, 13, 4)),
    (1201, "pt", "em março faz três anos", dt(2014, 3, 1), dt(2014, 4, 1), "", A),
    (1201, "pt-PT", "em março faz três anos", dt(2023, 3, 1), dt(2023, 4, 1), "", dt(2026, 10, 17, 12, 0)),
    (1202, "nl", "-1 uur", None, None, None, dt(1998, 1, 1, 0, 0)),
]


@pytest.mark.parametrize(
    "lang,text,start,end,remainder,anchor",
    [_case(FIXED_SPANS, issue, lang, text, start, end, rem, anchor)
     for issue, lang, text, start, end, rem, anchor in SPANS])
def test_span_rows(lang, text, start, end, remainder, anchor):
    found = extract_timespan(text, lang, anchor)
    if start is None:
        assert found is None
        return
    assert found is not None
    assert _matches(start, found.span.start.datetime())
    if end is not None:
        assert found.span.end.datetime() == end
    if remainder is not None:
        assert found.remainder == remainder


# issue, lang, text, expected length or None, expected remainder or None
DURATIONS = [

    (1203, "da", "1 århundrede", timedelta(days=36524), None),
    (1203, "da", "1 årtusinde", timedelta(days=365242), None),
    (1203, "gl", "1 século", timedelta(days=36524), None),
    (1203, "gl", "1 milenio", timedelta(days=365242), None),
    (1203, "es", "1 siglo", timedelta(days=36524), None),
    (1203, "es", "5 siglos", timedelta(days=182621), None),
    (1203, "es", "1 milenio", timedelta(days=365242), None),
    (1203, "es", "5 milenios", timedelta(days=1826212), None),
    (1203, "pt", "1 milénio", timedelta(days=365242), None),
    (1204, "az", "1.5 saat", timedelta(seconds=5400), None),
    (1204, "de", "weck mich in 3 wochen, 497 tagen und 391.6 sekunden", timedelta(days=518, seconds=391.6), None),
    (1204, "es", "7.5 segundos", timedelta(seconds=7.5), None),
    (1204, "fa", "7.5 ثانیه", timedelta(seconds=7.5), None),
    (1204, "gl", "1.5 horas", timedelta(seconds=5400), None),
    (1204, "pt", "2.5 horas", timedelta(seconds=9000), None),
    (1204, "pt", "0.1 segundo", timedelta(seconds=0.1), None),
    (1205, "pt", "daqui a duas horas", timedelta(hours=2), "daqui a"),
    (1205, "pt", "daqui a duas horas e trinta minutos", timedelta(minutes=150), "daqui a"),
    (1205, "pt", "a duas horas", timedelta(hours=2), "a"),
    (1205, "pt", "a duas horas e trinta minutos", timedelta(minutes=150), "a"),
]


@pytest.mark.parametrize(
    "lang,text,length,remainder",
    [_case((), issue, lang, text, length, rem)
     for issue, lang, text, length, rem in DURATIONS])
def test_duration_rows(lang, text, length, remainder):
    found = extract_duration(text, lang, anchor=ANCHOR)
    if length is None:
        assert found is None
        return
    assert found is not None
    assert found.duration == length
    if remainder is not None:
        assert found.remainder == remainder



# issue, lang, text, expected starts of the first three readings, anchor
CANDIDATES = [

    (1196, "pt", "às 9 uma hora antes do natal", [dt(2026, 12, 24, 21, 0), dt(2026, 12, 24, 23, 0), dt(2026, 12, 24, 9, 0)], dt(2026, 9, 25, 12, 0)),
    (1196, "en", "at 9 one hour before christmas", [dt(2026, 12, 24, 21, 0), dt(2026, 12, 24, 23, 0), dt(2026, 12, 24, 9, 0)], dt(2026, 9, 25, 12, 0)),
    (1196, "en", "at 6am 12 hours before easter monday", [dt(2027, 3, 28, 6, 0), dt(2027, 3, 28, 12, 0), dt(2027, 3, 28, 18, 0)], dt(2026, 9, 25, 12, 0)),
    (1196, "en", "a day and a half before easter monday at 9am", [dt(2027, 3, 27, 9, 0), dt(2027, 3, 27, 12, 0), dt(2027, 3, 27, 21, 0)], dt(2026, 9, 25, 12, 0)),
]


@pytest.mark.parametrize(
    "lang,text,starts,anchor",
    [_case((), issue, lang, text, starts, anchor)
     for issue, lang, text, starts, anchor in CANDIDATES])
def test_candidate_rows(lang, text, starts, anchor):
    found = extract_candidates(text, lang, anchor, limit=3)
    assert [c.span.start.datetime() for c in found] == starts
