"""An inflected day word names its day in bg, uk, pl, sk, sl, hr, sr, el, eo,
lt, et, sq, az, it, es, gl, pt, da, nb, nn and sv.

The forms are surfaces in each language's ``named_day_<off>.voc``, with the
source in the comment above them.  The expected day is the anchor, Tuesday
2017-06-27, plus the day offset.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

ROWS = [
    ("bg", "Днешната среща се проточи.", 0),
    ("bg", "Вчерашният дъжд наводни мазето.", -1),
    ("bg", "Не забравяй чадър за утрешната разходка.", 1),
    ("uk", "Сьогоднішня зустріч тривала довго.", 0),
    ("uk", "Я не дочитала вчорашньої статті.", -1),
    ("uk", "Готуйся до завтрашньої поїздки.", 1),
    ("pl", "Po wczorajszej burzy ogród jest mokry.", -1),
    ("pl", "Na dzisiejszym spotkaniu było tłoczno.", 0),
    ("pl", "Musimy przygotować jutrzejsze zebranie.", 1),
    ("sk", "Podklady k dnešnej porade sú hotové.", 0),
    ("hr", "O jučerašnjem razgovoru još razmišljam.", -1),
    ("hr", "Na današnjem sastanku bilo je napeto.", 0),
    ("hr", "Sutrašnji izlet bi se mogao otkazati.", 1),
    ("sr", "Na jučerašnjem sastanku smo se dogovorili.", -1),
    ("sr", "Јучерашњи разговор ме је изненадио.", -1),
    ("sr", "Sutrašnji izlet počinje rano.", 1),
    ("el", "Η σημερινή βροχή ήταν δυνατή.", 0),
    ("el", "Η αυριανή συναυλία μάλλον θα αναβληθεί.", 1),
    ("eo", "Mi ankoraŭ pensas pri la hieraŭa koncerto.", -1),
    ("lt", "Rytdienos šventei reikia pyrago.", 1),
    ("et", "Tänane koosolek venis pikaks.", 0),
    ("et", "Eilsest koosolekust on protokoll valmis.", -1),
    ("et", "Kas oled homseks koosolekuks valmis?", 1),
    ("sq", "Shiu i djeshëm zgjati gjithë natën.", -1),
    ("az", "Dünənki yağışdan sonra güllər təravətlidir.", -1),
    ("az", "Bugünkü görüşdə hamı danışdı.", 0),
    ("it", "Nella riunione odierna il progetto è stato approvato.", 0),
    ("es", "En la sesión hodierna se aprobó la reforma.", 0),
    ("gl", "Na sesión hodierna debateuse a reforma.", 0),
    ("pt", "Na sessão hodierna aprovou-se a reforma.", 0),
    ("da", "Har du læst gårsdagens avis?", -1),
    ("nb", "Har du lest gårsdagens avis?", -1),
    ("nb", "Vi trenger en sakliste for morgendagens styremøte.", 1),
    ("nn", "Eg gler meg til morgondagens fisketur.", 1),
    ("nn", "Gårsdagen var regnfull.", -1),
]


@pytest.mark.parametrize("lang,text,offset", ROWS)
def test_an_inflected_day_word_names_the_day(lang, text, offset):
    found = extract_timespan(text, lang, ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == ANCHOR.replace(hour=0, minute=0) + timedelta(days=offset)


def test_da_gaar_without_i_is_the_verb_and_leaves_the_weekday():
    found = extract_timespan(
        "Hvis alt går efter planen, maler vi køkkenet på fredag.", "da", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 30)


def test_da_i_gaar_is_still_yesterday():
    found = extract_timespan("Jeg så ham i går.", "da", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 6, 26)


def test_da_an_age_before_a_date_is_no_impossible_day():
    found = extract_timespan(
        "Min bedstemor fylder halvfems den 16. september.", "da", ANCHOR)
    assert found.span.start.datetime() == datetime(2017, 9, 16)


@pytest.mark.parametrize("lang,text", [
    ("it", "Il 32 aprile non esiste."),
    ("de", "Am 32. April ist nichts."),
])
def test_a_numeral_above_31_before_a_month_is_still_refused(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None


def test_da_gaar_alone_gives_no_date():
    assert extract_timespan("Alt går godt.", "da", ANCHOR) is None


PROBE_ANCHOR = datetime(2026, 11, 26, 12, 0)

# The "today's" adjectives also mean "present-day"; with no time or event
# noun beside them they give no date.
PRESENT_DAY = [
    ("pl", "dzisiejsza młodzież"),
    ("pl", "dzisiejsze czasy"),
    ("sk", "dnešná doba"),
    ("sk", "dnešný svet"),
    ("uk", "сьогоднішній світ"),
    ("bg", "днешното общество"),
    ("hr", "današnji svijet"),
    ("el", "σημερινή κοινωνία"),
    ("el", "η σημερινή εποχή"),
    ("sl", "današnji čas"),
    ("es", "La sociedad hodierna cambia deprisa."),
    ("it", "la società odierna"),
    ("pl", "dzisiejsza młodzież ma 20 lat"),
    ("uk", "сьогоднішній світ має 8 мільярдів людей"),
    ("bg", "днешното общество от 7 милиона"),
    ("el", "η σημερινή γενιά των 30 ετών"),
    ("pl", "dzisiejsza gazetka szkolna"),
    ("pl", "dzisiejszy meczet"),
    ("pl", "dzisiejsze programowanie"),
    ("hr", "današnji sateliti"),
    ("hr", "današnji programeri"),
    ("bg", "днешните програмисти"),
    ("sk", "dnešné hodinky"),
    ("sk", "dnešná doba je rýchla"),
    ("pl", "w dzisiejszych czasach"),
    ("hr", "u današnje vrijeme"),
    ("uk", "сьогоднішні уроки історії"),
    ("pl", "dzisiejsza młodzież, wiadomo, jest leniwa"),
]


@pytest.mark.parametrize("lang,text,start", [
    ("hr", "današnji svijet u 21. stoljeću", datetime(2000, 1, 1)),
    ("el", "σημερινή κοινωνία το 2026", datetime(2026, 1, 1)),
])
def test_a_present_day_adjective_leaves_the_other_date_to_read(lang, text, start):
    found = extract_timespan(text, lang, PROBE_ANCHOR)
    assert found.span.start.datetime() == start


@pytest.mark.parametrize("lang,text", PRESENT_DAY)
def test_the_present_day_sense_gives_no_date(lang, text):
    assert extract_timespan(text, lang, PROBE_ANCHOR) is None


CUED_TODAY = [
    ("pl", "dzisiejszy dzień"),
    ("sk", "dnešný deň"),
    ("el", "σημερινή ημέρα"),
    ("hr", "današnji dan"),
    ("uk", "сьогоднішній день"),
    ("pl", "dzisiejsze spotkanie"),
    ("es", "la sesión hodierna"),
    ("el", "η σημερινή συνάντηση"),
    ("uk", "сьогоднішня зустріч"),
    ("hr", "današnja sjednica"),
    ("bg", "днешната среща"),
    ("it", "l'odierna riunione"),
]


@pytest.mark.parametrize("lang,text", CUED_TODAY)
def test_a_time_or_event_noun_keeps_the_today_sense(lang, text):
    found = extract_timespan(text, lang, PROBE_ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 11, 26)


@pytest.mark.parametrize("lang,text", [
    ("pl", "wczorajsza gazeta"),
    ("hr", "jučerašnje novine"),
])
def test_yesterdays_paper_is_yesterday(lang, text):
    found = extract_timespan(text, lang, PROBE_ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 11, 25)
