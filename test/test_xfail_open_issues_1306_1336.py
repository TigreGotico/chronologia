"""Strict xfails for open issues 1306 to 1336.

Each row asserts the value the issue expects. Strict mode turns the run red
when a fix lands, so the fix removes the mark from its rows. The controls at
the end must keep their reading.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import (
    ImpossibleDateError,
    extract_duration,
    extract_event,
    extract_recurrence,
    extract_timespan,
)

ANCHOR = datetime(2026, 11, 22, 9, 0)
A_2017 = datetime(2017, 6, 27, 13, 4)
URL = "https://github.com/TigreGotico/chronologia/issues/"
WEEKDAYS = ((None, 0), (None, 1), (None, 2), (None, 3), (None, 4))  # Monday to Friday


def xfail(issue):
    return pytest.mark.xfail(strict=True, reason=URL + str(issue))


def rows(issue, entries):
    return [pytest.param(*entry, marks=xfail(issue)) for entry in entries]


def date_of(astro):
    return None if astro is None else astro.datetime().date()


@pytest.mark.parametrize("lang,text", rows(1306, [
    ("es", "un día de marzo"),
    ("pt", "um dia de março"),
    ("de", "ein Tag im März"),
    ("nl", "een dag van maart"),
    ("ca", "un dia de març"),
]))
def test_indefinite_article_names_no_day(lang, text):
    result = extract_timespan(text, lang, ANCHOR)
    if result is not None:
        assert result.span.start.datetime() == datetime(2027, 3, 1)
        assert result.span.end.datetime() == datetime(2027, 4, 1)


# (text, anchor, start, end)
RANGE_ENDS = rows(1309, [
    ("from early march to easter", ANCHOR, datetime(2026, 3, 1), datetime(2026, 4, 6)),
    ("from the last day of february to monday 1 march", datetime(2027, 3, 3, 15, 30), datetime(2027, 2, 28), datetime(2027, 3, 2)),
    ("from early march to 10 march at 5pm", ANCHOR, datetime(2026, 3, 1), datetime(2026, 3, 10, 17, 1)),
])


@pytest.mark.parametrize("text,anchor,start,end", RANGE_ENDS)
def test_range_end_is_first_occurrence_after_start(text, anchor, start, end):
    result = extract_timespan(text, "en", anchor)
    assert result is not None
    assert result.span.start.datetime() == start
    assert result.span.end.datetime() == end


# (lang, text, freq, byday, bymonthday, byhour)
HEADS = rows(1310, [
    ("pt-PT", "lembra-me às dez de cada dia útil", "WEEKLY", WEEKDAYS, (), (10,)),
    ("pt-PT", "às dez de cada dia de trabalho", "WEEKLY", WEEKDAYS, (), (10,)),
    ("pt-PT", "todos os dias úteis às 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("pt-PT", "todos os dias de semana às 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("pt-PT", "às dez de cada dia 15", "MONTHLY", (), (15,), (10,)),
    ("es-ES", "cada día laborable a las 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("es-ES", "cada día de trabajo a las 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("gl-ES", "cada día de traballo ás 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("ca-ES", "cada dia laborable a les 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("it-IT", "ogni giorno lavorativo alle 9", "WEEKLY", WEEKDAYS, (), (9,)),
    ("en-US", "every working day at 9", "WEEKLY", WEEKDAYS, (), (9,)),
])


@pytest.mark.parametrize("lang,text,freq,byday,bymonthday,byhour", HEADS)
def test_working_day_and_day_of_month_heads(lang, text, freq, byday, bymonthday, byhour):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result is not None
    rule = result.recurrence
    assert (rule.freq, rule.byday, rule.bymonthday, rule.byhour) == (freq, byday, bymonthday, byhour)


@pytest.mark.parametrize("lang,text", rows(1311, [
    ("es", "el 14 y 15 de mayo"),
    ("es", "el catorce y quince de mayo"),
    ("pt", "no dia 14 e 15 de maio"),
    ("pt", "nos dias 14 e 15 de maio"),
    ("it", "il 14 e 15 maggio"),
    ("fr", "le 14 et 15 mai"),
    ("fr", "le quatorze et quinze mai"),
    ("en", "on the 14th and 15th of may"),
    ("de", "am 14. und 15. Mai"),
]))
def test_list_of_two_days_reads_the_first(lang, text):
    result = extract_timespan(text, lang, ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(2027, 5, 14)


@pytest.mark.xfail(strict=True, reason=URL + "1311")
def test_list_of_two_days_primero_y_dos():
    result = extract_timespan("el primero y dos de mayo", "es", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(2027, 5, 1)


EVENINGS = datetime(2026, 11, 22, 23, 0)


@pytest.mark.parametrize("lang,text,start", rows(1312, [
    ("en", "at 8 hr. pm", datetime(2026, 11, 23, 20, 0)),
    ("es", "a las 8 hrs. de la noche", datetime(2026, 11, 23, 20, 0)),
    ("nl", "om 8 u. 's avonds", datetime(2026, 11, 23, 20, 0)),
    ("de", "um 8 Std. abends", datetime(2026, 11, 23, 20, 0)),
    ("pt", "às 5 p.m.", datetime(2026, 11, 23, 17, 0)),
    ("pt", "às 5 pm", datetime(2026, 11, 23, 17, 0)),
]))
def test_meridiem_after_abbreviated_hour_word(lang, text, start):
    result = extract_timespan(text, lang, EVENINGS)
    assert result is not None
    assert result.span.start.datetime() == start
    assert result.remainder == ""


# (lang, text, byhour, byminute)
CLOCK_RANGES = rows(1315, [
    ("pt", "todas as segundas das 9 às 17", (9,), ()),
    ("gl", "cada luns das 9 ás 17", (9,), ()),
    ("es", "cada lunes de 9 a 17 horas", (9,), ()),
    ("es", "todos los lunes a las 9 a 17", (9,), ()),
    ("en", "every monday at 9 to 5", (9,), ()),
    ("en", "every monday 9 to 5", (9,), ()),
])


@pytest.mark.parametrize("lang,text,byhour,byminute", CLOCK_RANGES)
def test_clock_range_in_a_recurrence(lang, text, byhour, byminute):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result is not None
    assert (result.recurrence.byhour, result.recurrence.byminute) == (byhour, byminute)
    assert result.remainder == ""


@pytest.mark.xfail(strict=True, reason=URL + "1315")
def test_monday_from_1_to_5_december_never_occurs():
    assert extract_recurrence("every monday from 1 to 5 december", "en", ANCHOR) is None


# (lang, text, byhour, until date or None)
UNTILS = rows(1316, [
    ("en", "every monday at 9 until 5 pm", (9,), None),
    ("en", "every monday at 9 until 5", (9,), None),
    ("en", "every monday at 9 until the 5th", (9,), date(2026, 12, 5)),
    ("en", "every monday at 9 to december 5", (9,), date(2026, 12, 5)),
])


@pytest.mark.parametrize("lang,text,byhour,until", UNTILS)
def test_until_bound_in_a_recurrence(lang, text, byhour, until):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result is not None
    assert result.recurrence.byhour == byhour
    assert date_of(result.recurrence.until) == until
    assert result.remainder == ""


@pytest.mark.xfail(strict=True, reason=URL + "1316")
def test_de_until_end_of_june_is_next_june():
    result = extract_recurrence("jeden Montag bis Ende Juni", "de", ANCHOR)
    assert result is not None
    until = date_of(result.recurrence.until)
    assert (until.year, until.month) == (2027, 6)


@pytest.mark.xfail(strict=True, reason=URL + "1316")
def test_until_bound_event_starts_on_monday():
    event = extract_event("every monday at 9 until 5 pm", "en", ANCHOR)
    assert event is not None
    assert event.span.start.datetime() == datetime(2026, 11, 23, 9, 0)


@pytest.mark.parametrize("text,control", rows(1320, [
    ("the 15th of february every year", "every year on the 15th of february"),
    ("every month on the first friday", "the first friday of every month"),
]))
def test_date_next_to_a_frequency_word(text, control):
    result = extract_recurrence(text, "en", ANCHOR)
    assert result is not None
    assert result.recurrence == extract_recurrence(control, "en", ANCHOR).recurrence
    assert result.remainder == ""


@pytest.mark.xfail(strict=True, reason=URL + "1321")
def test_nl_tot_en_met_is_a_weekday_range():
    long_form = extract_recurrence("elke maandag tot en met vrijdag", "nl", ANCHOR)
    short_form = extract_recurrence("elke maandag t/m vrijdag", "nl", ANCHOR)
    assert long_form is not None
    assert long_form.recurrence == short_form.recurrence


@pytest.mark.parametrize("lang,text", rows(1321, [
    ("en", "every monday to friday 9 am"),
    ("de", "jeden Montag bis Freitag 9 Uhr"),
]))
def test_weekday_range_before_a_clock(lang, text):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result is not None
    assert (result.recurrence.byday, result.recurrence.byhour) == (WEEKDAYS, (9,))


@pytest.mark.xfail(strict=True, reason=URL + "1321")
def test_de_month_after_a_clock_range_limits_the_rule():
    result = extract_recurrence("jeden Montag von 9 bis 17 Uhr im Dezember", "de", ANCHOR)
    assert result is not None
    assert (result.recurrence.bymonth, result.recurrence.byhour) == ((12,), (9,))
    assert result.remainder == ""


@pytest.mark.xfail(strict=True, reason=URL + "1321")
def test_pt_until_5_dez_is_an_end_date():
    result = extract_recurrence("todas as segundas de 9 até 5 dez", "pt", ANCHOR)
    assert result is not None
    assert result.recurrence.byhour == (9,)
    assert date_of(result.recurrence.until) == date(2026, 12, 5)


def test_monday_from_1_to_15_december_first_event():
    event = extract_event("every monday from 1 to 15 december", "en", ANCHOR)
    assert event is not None
    assert event.span.start.datetime().date() == date(2026, 12, 7)


@pytest.mark.parametrize("lang,text", rows(1322, [
    ("de", "jeden Montag 10 mal"),
    ("es", "cada lunes 10 veces"),
    ("fr", "toutes les lundis 10 fois"),
]))
def test_repeat_count_word(lang, text):
    result = extract_recurrence(text, lang, ANCHOR)
    assert result is not None
    assert result.recurrence.count == 10
    assert result.remainder == ""


@pytest.mark.xfail(strict=True, reason=URL + "1322")
def test_de_repeat_count_is_no_minute():
    result = extract_recurrence("jeden Montag um 9 Uhr 10 mal", "de", ANCHOR)
    assert result is not None
    rule = result.recurrence
    assert (rule.byhour, rule.byminute, rule.count) == ((9,), (), 10)


@pytest.mark.parametrize("text", rows(1324, [
    ("evening at 8 every day",),
    ("every day evening at 8",),
    ("every evening at 8",),
]))
def test_daypart_before_the_clock_in_a_daily_rule(text):
    result = extract_recurrence(text, "en", ANCHOR)
    assert result is not None
    assert (result.recurrence.freq, result.recurrence.byhour) == ("DAILY", (20,))
    assert result.remainder == ""


@pytest.mark.xfail(strict=True, reason=URL + "1324")
def test_daypart_before_the_clock_event_start():
    event = extract_event("evening at 8 every day", "en", ANCHOR)
    assert event is not None
    assert event.span.start.datetime() == datetime(2026, 11, 22, 20, 0)


@pytest.mark.parametrize("text,start", rows(1325, [
    ("the 23rd in the evening at 8", datetime(2026, 11, 23, 20, 0)),
    ("the 23rd at 8 in the evening", datetime(2026, 11, 23, 20, 0)),
    ("in 2 days evening at 8", datetime(2026, 11, 24, 20, 0)),
    ("in 2 days at 8 in the evening", datetime(2026, 11, 24, 20, 0)),
]))
def test_day_before_a_daypart_and_clock(text, start):
    result = extract_timespan(text, "en", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == start
    assert result.remainder == ""


@pytest.mark.parametrize("text", rows(1326, [
    ("at 9 the day before last",),
    ("the day after next 3 pm",),
    ("the day after tomorrow",),
    ("the day before yesterday at 9",),
]))
def test_day_word_is_no_length(text):
    assert extract_duration(text, "en", anchor=ANCHOR) is None


@pytest.mark.parametrize("text", rows(1327, [
    ("o ano de dois mil a dois mil e cinco",),
    ("os anos de dois mil a dois mil e cinco",),
    ("o ano de 2000 a 2005",),
]))
def test_pt_year_range_after_o_ano_de(text):
    result = extract_timespan(text, "pt", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(2000, 1, 1)
    assert result.span.end.datetime() == datetime(2006, 1, 1)
    assert result.remainder == ""


@pytest.mark.parametrize("lang,text", rows(1328, [
    ("en", "in february on the 30th"),
    ("de", "am 30. Februar um 9 Uhr"),
]))
def test_impossible_day_read_apart_declines(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None
    with pytest.raises(ImpossibleDateError, match="no 30th"):
        extract_timespan(text, lang, ANCHOR, impossible="raise")


@pytest.mark.xfail(strict=True, reason=URL + "1328")
def test_impossible_day_in_a_yearly_event_declines():
    assert extract_event("every year in february on the 30th", "en", ANCHOR) is None


@pytest.mark.parametrize("text", rows(1329, [
    ("anualmente às 9 a 29 de fevereiro",),
    ("todos os anos às 9 a 29 de fevereiro",),
]))
def test_pt_clock_before_a_day_in_a_yearly_rule(text):
    rule = extract_recurrence(text, "pt", ANCHOR).recurrence
    assert (rule.freq, rule.bymonth, rule.bymonthday, rule.byhour) == ("YEARLY", (2,), (29,), (9,))
    event = extract_event(text, "pt", ANCHOR)
    assert event.span.start.datetime() == datetime(2028, 2, 29, 9, 0)
    span = extract_timespan(text, "pt", ANCHOR)
    assert span.span.start.datetime() == datetime(2028, 2, 29, 9, 0)
    assert span.remainder == ""


@pytest.mark.parametrize("text,anchor,start,end", rows(1330, [
    ("from 1 february to 29 february", ANCHOR, datetime(2028, 2, 1), datetime(2028, 3, 1)),
    ("from 28 january to 29 february", ANCHOR, datetime(2028, 1, 28), datetime(2028, 3, 1)),
    ("from 28 january to 29 february", datetime(2096, 3, 1, 9, 0), datetime(2104, 1, 28), datetime(2104, 3, 1)),
]))
def test_yearless_range_ending_on_29_february(text, anchor, start, end):
    result = extract_timespan(text, "en", anchor)
    assert result is not None
    assert (result.span.start.datetime(), result.span.end.datetime()) == (start, end)


@pytest.mark.parametrize("text,seconds", rows(1331, [
    ("0030 minutes", 1800),
    ("for 0045 minutes", 2700),
    ("wait 0010 minutes", 600),
    ("in 0005 hours", 18000),
]))
def test_leading_zero_number_before_minutes_is_a_length(text, seconds):
    result = extract_duration(text, "en", anchor=ANCHOR)
    assert result is not None
    assert result.duration == timedelta(seconds=seconds)


@pytest.mark.xfail(strict=True, reason=URL + "1332")
def test_es_length_before_manana_is_tomorrow():
    event = extract_event("reunión de dos horas mañana", "es", ANCHOR)
    assert event is not None
    assert event.span.start.datetime().date() == date(2026, 11, 23)
    assert event.duration == timedelta(hours=2)


@pytest.mark.xfail(strict=True, reason=URL + "1332")
def test_es_length_before_esta_manana_is_this_morning():
    result = extract_timespan("reunión de dos horas esta mañana", "es", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(2026, 11, 22, 6, 0)
    assert result.span.end.datetime() == datetime(2026, 11, 22, 12, 0)
    assert result.remainder == "reunión de dos horas"


@pytest.mark.parametrize("text", rows(1333, [("last night at 11",), ("at 11 last night",)]))
def test_last_night_with_a_clock(text):
    result = extract_timespan(text, "en", ANCHOR)
    assert result is not None
    assert result.span.start.datetime() == datetime(2026, 11, 21, 23, 0)
    assert result.remainder == ""


# 1335: spaced half hour in ru and pl. (lang, text, start)
HALF_HOURS = rows(1335, [
    ("ru", "в пол восьмого", datetime(2017, 6, 27, 19, 30)),
    ("ru", "пол восьмого", datetime(2017, 6, 27, 19, 30)),
    ("ru", "в пол-одиннадцатого", datetime(2017, 6, 27, 22, 30)),
    ("ru", "в пол одиннадцатого", datetime(2017, 6, 27, 22, 30)),
    ("ru", "в пол девятого утра", datetime(2017, 6, 28, 8, 30)),
    ("pl", "w pół do ósmej", datetime(2017, 6, 27, 19, 30)),
    ("pl", "w pół do pierwszej", datetime(2017, 6, 28, 0, 30)),
    ("pl", "w pół do ósmej rano", datetime(2017, 6, 28, 7, 30)),
    ("pl", "spotkajmy się w pół do ósmej wieczorem", datetime(2017, 6, 27, 19, 30)),
])


@pytest.mark.parametrize("lang,text,start", HALF_HOURS)
def test_spaced_half_hour(lang, text, start):
    result = extract_timespan(text, lang, A_2017)
    assert result is not None
    assert result.span.start.datetime() == start


@pytest.mark.parametrize("lang,text", [
    ("ru", "упал на пол восьмого этажа"),
    ("ru", "пол второго этажа"),
    ("pl", "w pół drogi do domu"),
])
def test_half_without_a_clock_stays_no_clock(lang, text):
    assert extract_timespan(text, lang, A_2017) is None


# 1336: ordinal year in ru and uk. (lang, text, year)
ORDINAL_YEARS = rows(1336, [
    ("ru", "в две тысячи втором году", 2002),
    ("ru", "в две тысячи двадцать пятом году", 2025),
    ("ru", "в тысяча девятьсот девяносто пятом году", 1995),
    ("ru", "две тысячи двадцать пятый год", 2025),
    ("ru", "в тысяча девятьсот сорок пятом году", 1945),
    ("uk", "у дві тисячі другому році", 2002),
    ("uk", "у дві тисячі двадцять п'ятому році", 2025),
    ("uk", "тисяча дев'ятсот дев'яносто четвертий рік", 1994),
    ("uk", "у тисяча дев'ятсот сорок п'ятому році", 1945),
])


@pytest.mark.parametrize("lang,text,year", ORDINAL_YEARS)
def test_ordinal_year(lang, text, year):
    result = extract_timespan(text, lang, A_2017)
    assert result is not None
    assert result.span.start.datetime() == datetime(year, 1, 1)
    assert result.span.end.datetime() == datetime(year + 1, 1, 1)


@pytest.mark.parametrize("lang,text", [
    ("ru", "через две тысячи дней"),
    ("uk", "через дві тисячі днів"),
])
def test_two_thousand_days_stays_a_count(lang, text):
    result = extract_timespan(text, lang, A_2017)
    assert result is not None
    assert result.span.start.datetime() == A_2017 + timedelta(days=2000)
