"""Strict xfails for open issues 1206 to 1255.

Each row asserts the value the issue expects. Strict mode turns the run red
when a fix lands, so the fix removes the mark from its rows.
"""
from datetime import datetime, timedelta, timezone

import pytest

from chronologia import extract_duration, extract_event, extract_timespan

UTC = timezone.utc
A_2017 = datetime(2017, 6, 27, 13, 4)
A_2018 = datetime(2018, 6, 5, 9, 0)
A_2026 = datetime(2026, 1, 30, 10, 0)
URL = "https://github.com/TigreGotico/chronologia/issues/"


def xfail(issue):
    return pytest.mark.xfail(raises=AssertionError, strict=True, reason=URL + str(issue))


def duration_rows(issue, rows):
    return [pytest.param(*row, marks=xfail(issue)) for row in rows]


def span_rows(issue, rows):
    return [pytest.param(*row, marks=xfail(issue)) for row in rows]


# (lang, text, anchor, seconds, remainder or None)
DURATIONS = (
    duration_rows(1206, [("nl", "vijf minuten na het uur", A_2017, 300, "na het uur")])
    + duration_rows(1207, [
        ("he", "ספירה לאחור של שלוש שעות ועשר דקות", A_2017, 11400, None),
        ("he", "שלוש שעות ועשר דקות", A_2017, 11400, None),
    ])
    + duration_rows(1209, [
        ("ar", "ثانية واحدة", A_2017, 1, None),
        ("ar", "أسبوع واحد", A_2017, 604800, None),
        ("ar", "سنة واحدة", A_2017, 365 * 86400, None),
        ("ar", "شهرين", A_2017, 61 * 86400, None),
        ("ar", "سنتين", A_2017, 730 * 86400, None),
    ])
    + duration_rows(1210, [
        ("da", "ni og fyrre sekunder", A_2017, 49, None),
        ("kab", "mraw d yiwen n tesdidin", A_2017, 660, None),
        ("kab", "mraw d sin n tesdidin", A_2017, 720, None),
        ("kab", "ɛecrin d yiwen n tesdidin", A_2017, 1260, None),
    ])
    + duration_rows(1211, [
        ("kab", "tlatin tasint", A_2017, 30, None),
        ("sv", "starta en 9 minuters timer", A_2017, 540, "starta en timer"),
    ])
    + duration_rows(1231, [
        ("ms", "dua setengah jam lagi", A_2017, 9000, None),
        ("ms", "satu setengah jam lagi", A_2017, 5400, None),
        ("ms", "dua belas setengah hari lagi", A_2017, 1080000, None),
        ("id", "dua setengah jam lagi", A_2017, 9000, None),
        ("id", "satu setengah jam lagi", A_2017, 5400, None),
        ("id", "dua belas setengah hari lagi", A_2017, 1080000, None),
    ])
    + duration_rows(1236, [
        ("ar", "ثلاثون ثانية", A_2017, 30, None),
        ("ar", "ثلاثة أيام وخمس ساعات", A_2017, 277200, None),
        ("ar", "يومان وخمس ساعات", A_2017, 190800, None),
    ])
    + duration_rows(1239, [("kab", "sin mraw n tesdidin", A_2017, 720, None)])
    + duration_rows(1240, [
        ("sv", "två timmar och en kvart", A_2017, 8100, ""),
        ("sv", "hämta mig om två timmar och en kvart", A_2017, 8100, "hämta mig om"),
        ("sv", "två timmar och en halvtimme", A_2017, 9000, ""),
        ("en", "an hour and a quarter of an hour", A_2017, 4500, ""),
    ])
)


@pytest.mark.parametrize("lang,text,anchor,seconds,remainder", DURATIONS)
def test_duration(lang, text, anchor, seconds, remainder):
    result = extract_duration(text, lang, anchor=anchor)
    assert result is not None
    assert result.duration == timedelta(seconds=seconds)
    if remainder is not None:
        assert result.remainder == remainder


# (lang, text, anchor, start, end or None, remainder or None)
SPANS = (
    span_rows(1207, [
        ("he", "תעיר אותי בעוד שעה וחצי", A_2017, datetime(2017, 6, 27, 14, 34), None, None),
        ("he", "בעוד שעה ורבע", A_2017, datetime(2017, 6, 27, 14, 19), None, None),
        ("he", "בעוד שעתיים וחצי", A_2017, datetime(2017, 6, 27, 15, 34), None, None),
        ("he", "תעיר אותי בעוד שעה וחצי", A_2018, datetime(2018, 6, 5, 10, 30), None, None),
        ("he", "בעוד שעה ורבע", A_2018, datetime(2018, 6, 5, 10, 15), None, None),
        ("he", "בעוד שעתיים וחצי", A_2018, datetime(2018, 6, 5, 11, 30), None, None),
        ("he", "קבע פגישה ליום חמישי בשעה שתיים אחר הצהריים", A_2017, datetime(2017, 6, 29, 14, 0), None, None),
        ("he", "קבע פגישה ליום חמישי בשעה שתיים אחר הצהריים", A_2018, datetime(2018, 6, 7, 14, 0), None, None),
    ])
    + span_rows(1220, [
        ("fy", "om alve oere jûns", A_2026, datetime(2026, 1, 30, 23, 0), None, ""),
        ("fy", "om trije oere middeis", A_2026, datetime(2026, 1, 30, 15, 0), None, ""),
        ("fy", "om 8 oere jûns", A_2026, datetime(2026, 1, 30, 20, 0), None, ""),
    ])
    + span_rows(1225, [
        ("ca", text, A_2026, datetime(2026, 3, 3), datetime(2026, 3, 6), "")
        for text in (
            "des del 3 fins al 5 de març",
            "des del dia 3 fins al dia 5 de març",
        )
    ])
    + span_rows(1226, [
        ("fy", "fjouwer en tweintich oeren lyn", A_2026, datetime(2026, 1, 29, 10, 0), None, None),
        ("fy", "oer fjouwer en tweintich oeren", A_2026, datetime(2026, 1, 31, 10, 0), None, None),
    ])
    + span_rows(1228, [
        ("fy", "om 8 te begjinnen", A_2026, datetime(2026, 1, 30, 20, 0), None, "te begjinnen"),
    ])
    + span_rows(1229, [
        ("es", "desde el día 3 hasta las 5 de la tarde", A_2026, datetime(2026, 2, 3), None, None),
        ("es", "desde día 3 hasta las 5 de la tarde", A_2026, datetime(2026, 2, 3), None, None),
        ("es", "entre el día 3 y las 5 de la tarde", A_2026, datetime(2026, 2, 3), None, None),
        ("es", "desde el día 10 hasta las 8 de la noche", A_2026, datetime(2026, 2, 10), None, None),
        ("gl", "desde o día 10 ata as 8 da noite", A_2026, datetime(2026, 2, 10), None, None),
        ("it", "tra il giorno 10 e le 8 di sera", A_2026, datetime(2026, 2, 10), None, None),
        ("ca", "entre el dia 10 i les 8 del vespre", A_2026, datetime(2026, 2, 10), None, None),
    ])
    + span_rows(1234, [
        ("it", "stasera dieci meno un quarto", datetime(2026, 10, 17, 12, 0), datetime(2026, 10, 17, 21, 45), None, None),
    ])
    + span_rows(1254, [
        ("en", "9:30 utc", A_2017, datetime(2017, 6, 27, 21, 30, tzinfo=UTC), None, None),
    ] + [
        (lang, text, A_2017, None, datetime(2017, 6, 27, 21, 31, tzinfo=UTC), None)
        for lang, text in (
            ("en", "before 9:30 utc"),
            ("de", "vor 9:30 utc"),
            ("es", "antes de las 9:30 utc"),
            ("it", "prima delle 9:30 utc"),
            ("nl", "voor 9:30 utc"),
            ("ca", "abans de les 9:30 utc"),
            ("gl", "antes das 9:30 utc"),
        )
    ])
)


@pytest.mark.parametrize("lang,text,anchor,start,end,remainder", SPANS)
def test_timespan(lang, text, anchor, start, end, remainder):
    result = extract_timespan(text, lang, anchor)
    assert result is not None
    if start is not None:
        assert result.span.start.datetime() == start
    if end is not None:
        assert result.span.end.datetime() == end
    if remainder is not None:
        assert result.remainder == remainder


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=URL + "1253")
def test_aware_anchor_since_a_zoned_clock():
    anchor = datetime(2017, 6, 27, 12, 30, tzinfo=UTC)
    result = extract_timespan("since 1pm utc+2", "en", anchor)
    assert result is not None
    assert result.span.start.datetime() == datetime(2017, 6, 27, 11, 0, tzinfo=UTC)
    assert result.span.end.datetime() == anchor


EVENT_STARTS = [
    pytest.param("every holiday in Portugal at 3pm", datetime(2026, 11, 22, 9, 0), datetime(2026, 12, 1, 15, 0), id="clock", marks=xfail(1255)),
    pytest.param("every holiday in Portugal", datetime(2026, 12, 25, 10, 0), datetime(2026, 12, 25), id="christmas", marks=xfail(1255)),
    pytest.param("every holiday in Portugal", datetime(2026, 12, 1, 10, 0), datetime(2026, 12, 1), id="restauracao", marks=xfail(1255)),
]


@pytest.mark.parametrize("text,anchor,start", EVENT_STARTS)
def test_jurisdiction_holiday_event_start(text, anchor, start):
    event = extract_event(text, "en", anchor)
    assert event is not None
    assert event.span.start.datetime() == start
