# -*- coding: utf-8 -*-
"""Open-issue rows, 1014 to 1060.

Each row asserts the value its issue expects.  The mark is a strict xfail that
carries the issue URL, so the run turns red when a fix lands and the fix removes
the mark.  Every expected value comes from the issue text or from arithmetic on
the anchor, never from this library.

Anchor: Tuesday 2017-06-27 13:04, unless a row names its own.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_duration, extract_event, extract_timespan

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


# Rows that read right on dev: plain tests that keep the fix.
FIXED_SPANS = {
    "یک زنگ ساعت برای هفت صبح بگذار",
    "یک هشدار جدید برای ساعت هشت شب تنظیم کن",
    "tedd át a megbeszélést három órára",
    "laat me vanmiddag weten dat ik de loodgieter moet bellen",
    "väck mig i morgon bitti",
    "vilka larm har jag till i morgon",
    "duas horas e três quartos",
}
FIXED_LENGTHS = {
    "sæt en timer",
    "lav en timer på ti minutter",
    "ezarri hamar minutuko tenporizadore bat",
    "programatu bost minutuko tenporizadorea",
    "یک تایمر ده دقیقه\u200cای بگذار",
    "állíts be egy időzítőt öt percre",
    "kérek egy új időzítőt fél órára",
    "herinner me eraan elke weekendochtend om 8 uur de planten water te geven",
}


def _case(fixed, issue, *row):
    marks = () if row[1] in fixed else pytest.mark.xfail(raises=AssertionError,
        strict=True, reason=URL.format(issue))
    return pytest.param(
        *row, marks=marks, id="{}-{}-{}".format(issue, row[0], row[1]))


# issue, lang, text, expected start, expected end or None, expected remainder
# or None, anchor
SPANS = [

    (1014, "es", "léeme las alarmas de mañana", dt(2017, 6, 28), dt(2017, 6, 29), None, A),
    (1014, "gl", "amósame as alarmas de mañá", dt(2017, 6, 28), dt(2017, 6, 29), None, A),
    (1014, "es", "recuérdame ir al trabajo entre semana por la mañana a las 8", dt(2017, 6, 28, 8, 0), None, None, A),
    (1015, "da", "flyt aftalen i morgen til klokken femten", dt(2017, 6, 28, 15, 0), None, None, A),
    (1016, "de", "stelle bitte einen wecker für morgen früh um sechs", dt(2017, 6, 28, 6, 0), None, None, A),
    (1016, "de", "weck mich morgen früh um halb sieben", dt(2017, 6, 28, 6, 30), None, None, A),
    (1016, "de", "setze den frisörtermin auf halb neun", dt(2017, 6, 27, 20, 30), None, "setze den frisörtermin", A),
    (1017, "eu", "gogorarazi astegun guztietako arratsaldean amari deitzeko 6etan", dt(2017, 6, 27, 18, 0), None, None, A),
    (1018, "fa", "یک زنگ ساعت برای هفت صبح بگذار", dt(2017, 6, 28, 7, 0), None, None, A),
    (1018, "fa", "یک هشدار جدید برای ساعت هشت شب تنظیم کن", dt(2017, 6, 27, 20, 0), None, None, A),
    (1019, "fi", "herätä minut puoli seitsemältä", dt(2017, 6, 27, 18, 30), None, None, A),
    (1019, "fi", "aseta uusi herätys maanantaiksi kello seitsemän", dt(2017, 7, 3, 7, 0), None, None, A),
    (1020, "hu", "állíts be egy ébresztőt reggel hétre", dt(2017, 6, 28, 7, 0), None, None, A),
    (1020, "hu", "ébressz fel 7-kor egy hangoskönyvvel", dt(2017, 6, 27, 19, 0), None, None, A),
    (1020, "hu", "tedd át a megbeszélést három órára", dt(2017, 6, 27, 15, 0), None, None, A),
    (1022, "nl", "laat me vanmiddag weten dat ik de loodgieter moet bellen", date(2017, 6, 27), None, None, A),
    (1022, "nl", "zeg me iedere werkdagochtend dat ik mijn vitamines moet nemen", date(2017, 6, 28), None, None, A),
    (1022, "nl", "herinner me eraan elke weekendochtend om 8 uur de planten water te geven", dt(2017, 7, 1, 8, 0), None, None, A),
    (1025, "sv", "väck mig i morgon bitti", Within(dt(2017, 6, 28, 4, 0), dt(2017, 6, 28, 12, 0)), None, "väck mig", A),
    (1025, "sv", "vilka larm har jag till i morgon", dt(2017, 6, 28), dt(2017, 6, 29), None, A),
    (1027, "pt", "duas horas e três quartos", dt(2026, 1, 30, 14, 45), None, "", dt(2026, 1, 30, 10, 0)),
    (1032, "it", "0000", None, None, None, dt(2117, 9, 3, 13, 30)),
    (1032, "da", "20", dt(2117, 9, 3, 20, 0), None, None, dt(2117, 9, 3, 13, 30)),
    (1032, "it-IT", "tre quarti d'ora fa", dt(2026, 10, 17, 11, 15), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "it-IT", "mezzora fa", dt(2026, 10, 17, 11, 30), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "it-IT", "dalle 9 alle 11", dt(2026, 10, 17, 21, 0), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "it-IT", "alle 3 30", dt(2026, 10, 17, 15, 30), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "it-IT", "domani alle 8 15", dt(2026, 10, 18, 8, 15), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "it-IT", "le tre", dt(2026, 10, 17, 15, 0), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "it-IT", "il treno delle 8", dt(2026, 10, 17, 20, 0), None, None, dt(2026, 10, 17, 12, 0)),
    (1032, "es", "1 05 de la madrugada", dt(2024, 6, 16, 1, 5), None, None, dt(2024, 6, 15, 10, 0)),
    (1032, "es", "11 55 de la tarde", dt(2024, 6, 15, 23, 55), None, None, dt(2024, 6, 15, 10, 0)),
    # 1032 gives the minutes, not the half of the day: either next reading passes
    (1032, "ar", "الساعة الثالثة والثلث", (dt(2026, 7, 17, 15, 20), dt(2026, 7, 18, 3, 20)), None, None, dt(2026, 7, 17, 10, 0)),
    (1032, "ar", "الساعة التاسعة إلا ربعاً", (dt(2026, 7, 17, 20, 45), dt(2026, 7, 18, 8, 45)), None, None, dt(2026, 7, 17, 10, 0)),
    (1033, "es-ES", "mañana temprano", Within(dt(2026, 10, 18, 4, 0), dt(2026, 10, 18, 12, 0)), None, "", dt(2026, 10, 17, 12, 0)),
    (1033, "de", "morgen früh um 6 uhr", dt(2117, 9, 4, 6, 0), None, None, dt(2117, 9, 3, 13, 30)),
    (1033, "nb", "vekk meg i morgen tidlig", Within(dt(2017, 6, 28, 4, 0), dt(2017, 6, 28, 12, 0)), None, "vekk meg", A),
    (1033, "es", "ayer noche", Within(dt(1997, 12, 31, 18, 0), dt(1998, 1, 1, 0, 0)), None, None, dt(1998, 1, 1, 0, 0)),
    (1033, "es-ES", "la mañana de mañana", Within(dt(2026, 10, 18, 4, 0), dt(2026, 10, 18, 12, 0)), None, None, dt(2026, 10, 17, 12, 0)),
    (1033, "de-de", "was ist das Wetter am freitag morgen", Within(dt(2017, 6, 30, 4, 0), dt(2017, 6, 30, 12, 0)), None, None, A),
    (1040, "en", "from two thousand to three thousand dollars, from two thousand to two thousand and ten", dt(2000, 1, 1), dt(2011, 1, 1), None, A),
    (1042, "en", "two thousand. Then we moved", dt(2000, 1, 1), dt(2001, 1, 1), None, A),
    (1042, "en", "two thousand. Dollars were spent", dt(2000, 1, 1), dt(2001, 1, 1), None, A),
    (1049, "en", "mornings and evenings at 8", (dt(2026, 9, 26, 8, 0), dt(2026, 9, 25, 20, 0)), None, "", dt(2026, 9, 25, 12, 0)),
    (1049, "en", "morning and evening at 8", (dt(2026, 9, 26, 8, 0), dt(2026, 9, 25, 20, 0)), None, "", dt(2026, 9, 25, 12, 0)),
    (1051, "en", "good evening, set an alarm at 7", dt(2026, 9, 25, 19, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1051, "en", "good night, set an alarm at 7", dt(2026, 9, 25, 19, 0), None, None, dt(2026, 9, 25, 12, 0)),
    (1060, "nl", "om twee uur in de middag morgen", dt(2026, 1, 31, 14, 0), None, "", dt(2026, 1, 30, 10, 0)),
    (1060, "ca", "a dues hores a la tarda demà", dt(2026, 1, 31, 14, 0), None, "", dt(2026, 1, 30, 10, 0)),
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

    (1015, "da", "sæt en timer", None, None),
    (1015, "da", "lav en timer på ti minutter", timedelta(minutes=10), None),
    (1017, "eu", "ezarri hamar minutuko tenporizadore bat", timedelta(minutes=10), None),
    (1017, "eu", "programatu bost minutuko tenporizadorea", timedelta(minutes=5), None),
    (1018, "fa", "یک تایمر ده دقیقه‌ای بگذار", timedelta(minutes=10), None),
    (1020, "hu", "állíts be egy időzítőt öt percre", timedelta(minutes=5), None),
    (1020, "hu", "kérek egy új időzítőt fél órára", timedelta(minutes=30), None),
    (1022, "nl", "herinner me eraan elke weekendochtend om 8 uur de planten water te geven", None, None),
]


@pytest.mark.parametrize(
    "lang,text,length,remainder",
    [_case(FIXED_LENGTHS, issue, lang, text, length, rem)
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



# issue, lang, text, expected start, expected summary, anchor.  An event whose
# text names a clock has no explicit length.
EVENTS = [

    (1026, "fr", "dîner neuf heures et demie le soir demain", dt(2026, 1, 31, 21, 30), "dîner", dt(2026, 1, 30, 10, 0)),
    (1026, "pt", "jantar nove horas e meia de noite amanhã", dt(2026, 1, 31, 21, 30), "jantar", dt(2026, 1, 30, 10, 0)),
]


@pytest.mark.parametrize(
    "lang,text,start,summary,anchor",
    [_case((), issue, lang, text, start, summary, anchor)
     for issue, lang, text, start, summary, anchor in EVENTS])
def test_event_rows(lang, text, start, summary, anchor):
    event = extract_event(text, lang, anchor)
    assert event is not None
    assert event.duration is None
    assert event.span.start.datetime() == start
    assert event.summary == summary
