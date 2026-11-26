# -*- coding: utf-8 -*-
"""Open-issue rows, 987 to 1013.

Each row asserts the value its issue expects.  The mark is a strict xfail that
carries the issue URL, so the run turns red when a fix lands and the fix removes
the mark.  Every expected value comes from the issue text or from arithmetic on
the anchor, never from this library.

Anchor: Tuesday 2017-06-27 13:04, unless a row names its own.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan, extract_timespans

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
    "a las 9, esta noche",
    "el darrer dilluns de març",
    "lo zaguer luns de marzo",
    "avísame de luns a venres pola mañá sobre as 7",
    "at 8 tonight",
    "remind me to call the bank tomorrow morning",
    "deg snat n dduṛt",
    "tafsut i d-iteddun",
}


def _case(fixed, issue, *row):
    marks = () if row[1] in fixed else pytest.mark.xfail(
        strict=True, reason=URL.format(issue))
    return pytest.param(
        *row, marks=marks, id="{}-{}-{}".format(issue, row[0], row[1]))


# issue, lang, text, expected start, expected end or None, expected remainder
# or None, anchor
SPANS = [

    (987, "ru", "поставь напоминание на восемь вечера", dt(2017, 6, 27, 20, 0), None, None, A),
    (987, "uk", "на сьому", dt(2017, 6, 27, 19, 0), None, None, A),
    (987, "ru", "создай новый будильник на завтра на шесть", dt(2017, 6, 28, 6, 0), None, None, A),
    (989, "fa", "این سرمای شدید هوا ادامه پیدا می کند", None, None, None, A),
    (989, "fa", "بیرون باد می وزد یا هوا آرام است", None, None, None, A),
    (989, "fa", "این فیلم طول می کشد", None, None, None, A),
    (989, "fa", "می خوام برم", None, None, None, A),
    (989, "fa", "می خواهم بدانم هوای فردا قرار است چطور باشد", dt(2017, 6, 28), None, None, A),
    (989, "fa", "دمای هوا صبح دوشنبه چند درجه می شود", date(2017, 7, 3), None, None, A),
    (992, "oc", "Farà calor aquela nuèch", date(2017, 6, 27), None, None, A),
    (992, "oc", "Aquesta nuèch i aurà una bruma plan espessa?", date(2017, 6, 27), None, None, A),
    (992, "an", "pasau manyana", date(2017, 6, 29), None, None, A),
    (992, "an", "antes d'ahiere", date(2017, 6, 25), None, None, A),
    (992, "eu", "duela aste bat", date(2017, 6, 20), None, None, A),
    (992, "kab", "deg 3 wussan", date(2017, 6, 30), None, None, A),
    (992, "kab", "3 wussan aya", date(2017, 6, 30), None, None, A),
    (992, "kab", "deg snat n dduṛt", date(2017, 7, 11), None, None, A),
    (992, "fi", "heinäkuun ensimmäinen viikko", date(2017, 7, 3), None, None, A),
    (992, "fa", "هفته اول ژوئیه", date(2017, 7, 3), None, None, A),
    (992, "an", "qué hora será d'aquí a una hora", dt(2017, 6, 27, 14, 4), None, None, A),
    (993, "an", "lo proximo verano", Within(dt(2018, 6, 1), dt(2018, 6, 22)), None, "", A),
    (993, "an", "la primavera proxima", Within(dt(2018, 3, 1), dt(2018, 3, 22)), None, "", A),
    (993, "an", "a l'anyo proximo", dt(2018, 1, 1), None, None, A),
    (993, "an", "la semana proxima", dt(2017, 7, 3), None, None, A),
    (993, "an", "mes proximo", dt(2017, 7, 1), None, None, A),
    (993, "da", "sidste oktober", dt(2016, 10, 1), None, "", A),
    (993, "da", "til foråret", Within(dt(2018, 3, 1), dt(2018, 3, 22)), None, "", A),
    (993, "hu", "tavaly ősszel", Within(dt(2016, 9, 1), dt(2016, 9, 24)), None, "", A),
    (993, "hu", "2024 tavasza", Within(dt(2024, 3, 1), dt(2024, 3, 22)), None, "", A),
    (993, "hu", "1999 nyara", Within(dt(1999, 6, 1), dt(1999, 6, 22)), None, "", A),
    (993, "kab", "tafsut i d-iteddun", Within(dt(2018, 3, 1), dt(2018, 3, 22)), None, "", A),
    (994, "da", "fredag, den femtende marts, to tusind og fire og tyve", dt(2024, 3, 15), None, "", A),
    (997, "en", "when does it start getting light in the morning", dt(2017, 6, 28, 6, 0), dt(2017, 6, 28, 12, 0), None, A),
    (997, "pt-BR", "Que horas começa a clarear de manhã?", dt(2017, 6, 28, 6, 0), dt(2017, 6, 28, 12, 0), None, A),
    (997, "es", "¿A qué horas empieza a aclarar por la mañana?", dt(2017, 6, 28, 6, 0), dt(2017, 6, 28, 12, 0), None, A),
    (997, "da", "Hvad tid på morgenen gryr dagen ovre i London?", dt(2017, 6, 28, 5, 0), dt(2017, 6, 28, 10, 0), None, A),
    (997, "en", "let the upcoming alarm come back each morning", date(2017, 6, 28), None, None, A),
    (997, "es", "necesito que suene una alarma por la mañana", date(2017, 6, 28), None, None, A),
    (997, "pt", "acorda-me com música de manhã", date(2017, 6, 28), None, None, A),
    (997, "fi", "tarvitsen herätyksen aamulla", date(2017, 6, 28), None, None, A),
    (997, "pt", "à tarde", dt(2023, 1, 16, 12, 0), dt(2023, 1, 16, 19, 0), None, dt(2023, 1, 15, 21, 0)),
    (1001, "en", "dinner at 8, breakfast at 7 am", dt(2017, 6, 27, 20, 0), None, None, A),
    (1001, "en", "at 8 or at 9 pm", dt(2017, 6, 27, 20, 0), None, None, A),
    (1001, "en", "at 8 we watch the morning show", dt(2017, 6, 27, 20, 0), None, None, A),
    (1001, "es-ES", "a las 9, esta noche", dt(2026, 1, 5, 21, 0), None, None, dt(2026, 1, 5, 6, 0)),
    (1002, "en", "at 8 tonight", dt(2017, 6, 27, 20, 0), None, "", A),
    (1002, "es-ES", "tarde a las 4:30", dt(2026, 10, 17, 16, 30), None, "", dt(2026, 10, 17, 12, 0)),
    (1004, "en", "how many days before christmas", dt(2017, 12, 25), None, None, A),
    (1004, "fr", "il reste combien de jours avant le 15 mai", dt(2018, 5, 15), None, None, A),
    (1004, "fr", "combien de jours il y a du 1er mars au 15 avril", dt(2018, 3, 1), dt(2018, 4, 16), None, A),
    (1004, "ru", "сколько ещё дней до 1 января", dt(2018, 1, 1), None, None, A),
    (1004, "ru", "сколько дней до 31 октября", dt(2017, 10, 31), None, None, A),
    (1004, "pl", "która będzie godzina za godzinę", dt(2017, 6, 27, 14, 4), None, None, A),
    (1004, "pt", "daqui a uma hora, horas vão ser", dt(2017, 6, 27, 14, 4), None, None, A),
    (1005, "ca", "el darrer dilluns de març", dt(2017, 3, 27), None, "", A),
    (1005, "an", "lo zaguer luns de marzo", dt(2017, 3, 27), None, "", A),
    (1005, "fa", "آخرین دوشنبه مارس", dt(2017, 3, 27), None, "", A),
    (1005, "kab", "letnayen aneggaru n meɣres", dt(2017, 3, 27), None, "", A),
    (1008, "en", "move my alarm to 9", dt(2017, 6, 27, 21, 0), None, None, A),
    (1008, "en", "can you move my 8 am alarm to 9:15", dt(2017, 6, 28, 9, 15), None, None, A),
    (1008, "en", "move my alarm from eight to nine thirty", dt(2017, 6, 27, 20, 0), None, None, A),
    (1008, "it", "imposta una sveglia per le 7", dt(2017, 6, 27, 19, 0), None, None, A),
    (1008, "it", "programma una sveglia per le sette di domani", dt(2017, 6, 28, 7, 0), None, None, A),
    (1008, "pt", "mova o meu alarme das sete para as oito", dt(2017, 6, 27, 19, 0), None, None, A),
    (1009, "ca", "recorda'm que vagi a la feina els matins a les 8", dt(2017, 6, 28, 8, 0), None, None, A),
    (1009, "pt", "lembra-me todas as manhãs de tomar o medicamento às 8", dt(2017, 6, 28, 8, 0), None, None, A),
    (1009, "eu", "gogorarazi goizetan medikazioa hartzeko 8etan", dt(2017, 6, 28, 8, 0), None, None, A),
    (1009, "fi", "muistuta minua arkiaamuisin kahdeksalta ottamaan lääkkeeni", dt(2017, 6, 28, 8, 0), None, None, A),
    (1009, "es", "recuérdame cada mañana tomar mi medicina a las 8", dt(2017, 6, 28, 8, 0), None, None, A),
    (1010, "es", "de lunes a viernes a las ocho de la mañana avísame", dt(2017, 6, 28, 8, 0), None, None, A),
    (1010, "pt", "me lembre de regar as plantas toda segunda e sexta às 8 da manhã", dt(2017, 6, 30, 8, 0), None, None, A),
    (1010, "it", "ricordami di chiamare mia madre tutte le sere dal lunedì al venerdì alle 18", dt(2017, 6, 27, 18, 0), None, None, A),
    (1010, "kab", "seg letnayen ar lǧemɛa ɣef tesɛa n ṣṣbeḥ, smektay-iyi ad ẓreɣ imaylen-iw", dt(2017, 6, 28, 9, 0), None, None, A),
    (1011, "es", "avíseme de lunes a viernes por la mañana tipo 7", dt(2017, 6, 28, 7, 0), None, None, A),
    (1011, "gl", "avísame de luns a venres pola mañá sobre as 7", dt(2017, 6, 28, 7, 0), None, None, A),
    (1011, "ca", "avisa'm de dilluns a divendres al matí cap a les 7", dt(2017, 6, 28, 7, 0), None, None, A),
    (1012, "pt", "às 10 30", dt(2017, 6, 27, 22, 30), None, "", A),
    (1012, "fa", "در ساعت 10 30", dt(2017, 6, 27, 22, 30), None, None, A),
    (1013, "en", "remind me to call the bank tomorrow morning", dt(2017, 6, 28, 6, 0), dt(2017, 6, 28, 12, 0), None, A),
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

    (992, "an", "tres segundos", timedelta(seconds=3), None),
    (1004, "es", "la semana pasada", None, None),
    (1004, "es", "la semana que viene", None, None),
    (1004, "gl", "a semana pasada", None, None),
    (1004, "hu", "ezen a héten", None, None),
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


# issue, lang, text, expected char_span of the first mention
MENTIONS = [
    (996, "pt", "na sexta-feira", (0, 14)),
    (996, "gl", "o venres", (0, 8)),
]


@pytest.mark.parametrize(
    "lang,text,char_span",
    [_case((), issue, lang, text, cs) for issue, lang, text, cs in MENTIONS])
def test_mention_rows(lang, text, char_span):
    found = extract_timespans(text, lang, ANCHOR)
    assert found
    assert found[0].char_span == char_span
