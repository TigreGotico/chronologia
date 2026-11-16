"""A length before "before"/"after" is the date's offset, not the event's width.

"dentist three days before christmas" is one day, 22 December.  The event
reader must not take "three days" as the length and date the event from what
is left ("before christmas").  A length with "for" stays a length.  Anchor
30 January 2026, 10:00: the kalends (1st), nones (7th) and ides (15th) of the
months below are still ahead in 2026.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_event, extract_timespan

ANCHOR = datetime(2026, 1, 30, 10, 0)


@pytest.mark.parametrize("lang, text, summary, day", [
    ("en", "dentist three days before christmas", "dentist", datetime(2026, 12, 22)),
    ("en", "party 2 days after christmas", "party", datetime(2026, 12, 27)),
    ("en", "team dinner a week before the ides of march", "team dinner",
     datetime(2026, 3, 8)),
    ("en", "pay the rent 3 days after the kalends of april", "pay the rent",
     datetime(2026, 4, 4)),
    ("en", "3 days before the kalends of april", "", datetime(2026, 3, 29)),
    ("en", "the day before the nones of july", "", datetime(2026, 7, 6)),
    ("fr", "dîner 2 jours après les calendes d'avril", "dîner", datetime(2026, 4, 3)),
])
def test_offset_dates_the_event(lang, text, summary, day):
    ev = extract_event(text, lang, anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.duration) == (summary, day, None)


def test_offset_from_now_dates_the_event():
    ev = extract_event("dentist in 3 days", "en", anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.duration) == (
        "dentist", ANCHOR + timedelta(days=3), None)


@pytest.mark.parametrize("text, summary, start, length", [
    # controls: "for" makes the number a length
    ("holiday for 3 days from tomorrow", "holiday", datetime(2026, 1, 31),
     timedelta(days=3)),
    ("call mom at 5pm for 10 minutes", "call mom", datetime(2026, 1, 30, 17),
     timedelta(minutes=10)),
])
def test_length_with_for_stays_a_length(text, summary, start, length):
    ev = extract_event(text, "en", anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.span.end, ev.duration) == (
        summary, start, start + length, length)


MONDAY = datetime(2026, 1, 26, 10, 0)


@pytest.mark.parametrize("lang, text, anchor, summary, day, hours", [
    # "uur" and "heures" are a clock hour and a length: Larousse "heure",
    # en.wiktionary nl "uur". Without a marker the number is the length.
    ("fr", "réunion de deux heures demain", ANCHOR, "réunion",
     datetime(2026, 1, 31), 2),
    ("fr", "un cours de deux heures vendredi", MONDAY, "cours",
     datetime(2026, 1, 30), 2),
    ("fr", "je travaille trois heures demain", ANCHOR, "je travaille",
     datetime(2026, 1, 31), 3),
    ("nl", "vergadering van twee uur morgen", ANCHOR, "vergadering",
     datetime(2026, 1, 31), 2),
    ("nl", "ik werk drie uur morgen", ANCHOR, "ik werk",
     datetime(2026, 1, 31), 3),
    # a day word or a month that holds an "after", "before" or "in" word is
    # still one date: Larousse "après-demain", the day after tomorrow
    ("fr", "réunion de deux heures après-demain", ANCHOR, "réunion",
     datetime(2026, 2, 1), 2),
    ("fr", "réunion de deux heures après demain", ANCHOR, "réunion",
     datetime(2026, 2, 1), 2),
    ("fr", "j'ai travaillé deux heures avant-hier", ANCHOR, "j ai travaillé",
     datetime(2026, 1, 28), 2),
    ("fr", "j'ai travaillé deux heures avant hier", ANCHOR, "j ai travaillé",
     datetime(2026, 1, 28), 2),
    ("fr", "réunion de deux heures en mars", ANCHOR, "réunion",
     datetime(2026, 3, 1), 2),
    ("nl", "vergadering van twee uur in maart", ANCHOR, "vergadering",
     datetime(2026, 3, 1), 2),
])
def test_a_length_without_an_offset_marker_stays_a_length(
        lang, text, anchor, summary, day, hours):
    ev = extract_event(text, lang, anchor=anchor)
    length = timedelta(hours=hours)
    assert (ev.summary, ev.span.start, ev.span.end, ev.duration) == (
        summary, day, day + length, length)


@pytest.mark.parametrize("lang, text, date_word, start, hours", [
    # The whole text reads "dos horas en" as "in two hours" and leaves the
    # month; the rest reads the month.  1 March 2026 is the next March.
    ("es", "reunión de dos horas en marzo", "marzo", datetime(2026, 3, 1), 2),
    ("es", "reunión de dos horas en abril", "abril", datetime(2026, 4, 1), 2),
    ("es", "clase de dos horas en mayo", "mayo", datetime(2026, 5, 1), 2),
    ("es", "trabajo tres horas en marzo", "marzo", datetime(2026, 3, 1), 3),
    # meteorological summer starts on 1 June (NOAA NCEI, "Meteorological
    # Versus Astronomical Seasons")
    ("es", "reunión de dos horas en verano", "verano", datetime(2026, 6, 1),
     2),
    ("gl", "reunión de dúas horas en marzo", "marzo", datetime(2026, 3, 1), 2),
    ("ro", "ședință de două ore în martie", "martie", datetime(2026, 3, 1), 2),
    # The whole text reads "twee uur" as 02:00 and leaves "morgen".
    ("nl", "vergadering van twee uur na het werk morgen", "morgen",
     datetime(2026, 1, 31), 2),
    ("nl", "vergadering van twee uur na school morgen", "morgen",
     datetime(2026, 1, 31), 2),
    ("nl", "twee uur sporten na het eten morgen", "morgen",
     datetime(2026, 1, 31), 2),
    ("nl", "vergadering van twee uur na de lunch morgen", "morgen",
     datetime(2026, 1, 31), 2),
    ("nl", "vergadering van twee uur in de middag morgen", "morgen",
     extract_timespan("in de middag morgen", "nl", anchor=ANCHOR).span.start,
     2),
])
def test_a_length_the_whole_text_reads_as_a_time_keeps_the_rest_date(
        lang, text, date_word, start, hours):
    ev = extract_event(text, lang, anchor=ANCHOR)
    assert (ev.span.start, ev.duration) == (start, timedelta(hours=hours))
    assert date_word not in ev.summary.split()


@pytest.mark.parametrize("jurisdiction, day", [
    # Christmas 2026 is a Friday.  GB moves Boxing Day (Saturday) to Monday
    # 28 December, so its second business day is the 30th; US works the 28th.
    ("GB", datetime(2026, 12, 30)),
    ("US", datetime(2026, 12, 29)),
])
def test_a_length_before_a_business_day_date_keeps_the_jurisdiction(
        jurisdiction, day):
    ev = extract_event("a 2 hour meeting 2 business days after christmas", "en",
                       anchor=ANCHOR, jurisdiction=jurisdiction)
    assert (ev.summary, ev.span.start, ev.duration) == (
        "meeting", day, timedelta(hours=2))


def test_nl_quarter_hour_offset_reads_like_its_english_form():
    """Dutch "een kwartier" is the unit quarter_hour; it reads as the
    English "15 minutes" does and raises nothing."""
    for nl, en in [
        ("we eten een kwartier na kerstmis", "we eat 15 minutes after christmas"),
        ("een kwartier voor kerstmis bellen",
         "15 minutes before christmas call"),
    ]:
        got = extract_event(nl, "nl", anchor=ANCHOR)
        want = extract_event(en, "en", anchor=ANCHOR)
        assert (got.span.start, got.span.end, got.duration) == (
            want.span.start, want.span.end, want.duration)


def test_nl_quarter_hour_before_christmas_is_the_day_before():
    ev = extract_event("een kwartier voor kerstmis bellen", "nl", anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.duration) == (
        "bellen", datetime(2026, 12, 24), None)


def test_a_failing_whole_text_read_does_not_raise(monkeypatch):
    """The exploratory whole-text read must not take the event down."""
    import chronologia.extract as extract
    real = extract.extract_timespan
    calls = []

    def flaky(text, *args, **kwargs):
        calls.append(text)
        if len(calls) == 1:
            raise ValueError("unsupported offset unit")
        return real(text, *args, **kwargs)

    monkeypatch.setattr(extract, "extract_timespan", flaky)
    ev = extract_event("dentist for 2 hours tomorrow", "en", anchor=ANCHOR)
    assert (ev.summary, ev.duration) == ("dentist", timedelta(hours=2))


@pytest.mark.parametrize("nl, en", [
    ("een kwartier na kerstmis", "15 minutes after christmas"),
    ("een kwartier voor kerstmis", "15 minutes before christmas"),
    ("twee kwartier na kerstmis", "30 minutes after christmas"),
])
def test_nl_quarter_hour_offset_spans_like_its_english_form(nl, en):
    got = extract_timespan(nl, "nl", anchor=ANCHOR)
    want = extract_timespan(en, "en", anchor=ANCHOR)
    assert (got.span.start, got.span.end) == (want.span.start, want.span.end)


@pytest.mark.parametrize("lang, text, start", [
    # an offset from now has no "before" or "after" word; the length is the
    # offset (anchor Friday 30 January 2026, 10:00)
    ("an", "dentro de 3 semanas", datetime(2026, 2, 20, 10)),
    ("id", "1 jam lagi", datetime(2026, 1, 30, 11)),
    ("vi", "7 ngày trước", datetime(2026, 1, 23, 10)),
    ("it", "fra un quarto d'ora", datetime(2026, 1, 30, 10, 15)),
    # a bare clock hour has no date to carry the event: "2 heures" stays 02:00
    ("fr", "2 heures", datetime(2026, 1, 31, 2)),
    ("nl", "15 uur", datetime(2026, 1, 30, 15)),
    # "saat 12" is as wide as "3 gün", but it is not the length's words
    ("tr", "3 gün önce saat 12", datetime(2026, 1, 27, 12)),
    ("az", "3 gün əvvəl saat 9", datetime(2026, 1, 27, 9)),
    # a clock time wider than the number and unit is a clock time
    ("fr", "dîner cinq heures du matin demain", datetime(2026, 1, 31, 5)),
])
def test_an_offset_without_a_marker_word_is_the_date(lang, text, start):
    ev = extract_event(text, lang, anchor=ANCHOR)
    assert (ev.span.start, ev.duration) == (start, None)


def test_a_clock_like_length_before_a_date_is_still_an_offset():
    """fr "deux heures avant midi" is 10:00: the hours are the offset."""
    ev = extract_event("réunion deux heures avant midi", "fr", anchor=ANCHOR)
    assert (ev.summary, ev.span.start, ev.duration) == (
        "réunion", datetime(2026, 1, 30, 10), None)
