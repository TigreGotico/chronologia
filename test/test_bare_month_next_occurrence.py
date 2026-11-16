"""A month named without a day is its next occurrence.

prefer_future means the next occurrence strictly after the anchor, and a month
is a span: the month that holds the anchor is this month, and a month that has
ended is next year's.  At the Tuesday 27 June 2017 anchor, January and March
have ended, so they are the 2018 months; June holds the anchor and July is
ahead, so both stay in 2017.  An explicit year is kept as written.

The Hebrew months take the same rule in their own calendar.  1 Nisan 5778 is
17 March 2018, 14 days before the first Passover day, 31 March 2018 (15
Nisan).  1 Tishrei 5778, Rosh Hashanah, is 21 September 2017.

A relative marker moves the bare reading.  "last October" is the latest
October that has ended, October 2016; "last June" said in June is June 2016.
"next June" said in June is June 2018, and "next July" is July 2017.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_timespans
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _span(text, lang):
    r = extract_timespan(text, lang, ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r


@pytest.mark.parametrize("text,lang,year,month", [
    ("january", "en", 2018, 1),
    ("in january", "en", 2018, 1),
    ("march", "en", 2018, 3),
    ("june", "en", 2017, 6),
    ("july", "en", 2017, 7),
    ("janvier", "fr", 2018, 1),
    ("en janvier", "fr", 2018, 1),
    ("juin", "fr", 2017, 6),
    ("im Januar", "de", 2018, 1),
    ("janeiro", "pt", 2018, 1),
    ("en enero", "es", 2018, 1),
    ("januar", "sl", 2018, 1),
    ("junij", "sl", 2017, 6),
    ("január", "hu", 2018, 1),
    ("styczeń", "pl", 2018, 1),
    ("w styczniu", "pl", 2018, 1),
    ("в январе", "ru", 2018, 1),
    ("у січні", "uk", 2018, 1),
])
def test_bare_month_is_its_next_occurrence(text, lang, year, month):
    r = _span(text, lang)
    nyear, nmonth = (year, month + 1) if month < 12 else (year + 1, 1)
    assert r.span.start == AstroDate(year, month, 1)
    assert r.span.end == AstroDate(nyear, nmonth, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text,lang,year,month", [
    ("january 2017", "en", 2017, 1),
    ("janvier 2017", "fr", 2017, 1),
])
def test_explicit_year_is_kept(text, lang, year, month):
    assert _span(text, lang).span.start == AstroDate(year, month, 1)


@pytest.mark.parametrize("text,lang,start", [
    ("nisan", "en", AstroDate(2018, 3, 17)),
    ("tishrei", "en", AstroDate(2017, 9, 21)),
])
def test_calendar_month_is_its_next_occurrence(text, lang, start):
    assert _span(text, lang).span.start == start


@pytest.mark.parametrize("text,lang,year,month", [
    ("last october", "en", 2016, 10),
    ("last june", "en", 2016, 6),
    ("next june", "en", 2018, 6),
    ("next july", "en", 2017, 7),
    ("в прошлом октябре", "ru", 2016, 10),
    ("в следующем январе", "ru", 2018, 1),
    ("у минулому жовтні", "uk", 2016, 10),
    ("im letzten Oktober", "de", 2016, 10),
])
def test_relative_month(text, lang, year, month):
    r = _span(text, lang)
    assert r.span.start == AstroDate(year, month, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text,lang,year,month,remainder", [
    ("напомни мне в январе", "ru", 2018, 1, "напомни мне"),
    ("remind me in march", "en", 2018, 3, "remind me"),
])
def test_bare_month_inside_a_request(text, lang, year, month, remainder):
    r = _span(text, lang)
    assert r.span.start == AstroDate(year, month, 1)
    assert r.remainder == remainder


@pytest.mark.parametrize("text,lang", [
    ("march of this year", "en"),
    ("march this year", "en"),
    ("в марте этого года", "ru"),
    ("у березні цього року", "uk"),
    ("w marcu tego roku", "pl"),
    ("em março deste ano", "pt"),
    ("en marzo de este año", "es"),
    ("en mars cette année", "fr"),
    ("im März dieses Jahres", "de"),
    ("mars dernier", "fr"),
    ("en mars dernier", "fr"),
    ("marzo pasado", "es"),
    ("em março passado", "pt"),
    ("marzo scorso", "it"),
])
def test_month_with_this_year_or_a_postposed_last(text, lang):
    # "this year" names the anchor's year, so March 2017 has ended and is
    # still March 2017.  A postposed "last" ("mars dernier") is the latest
    # March that has ended, the same month.
    r = _span(text, lang)
    assert r.span.start == AstroDate(2017, 3, 1)
    assert r.span.end == AstroDate(2017, 4, 1)
    assert r.remainder == ""


@pytest.mark.parametrize("text,date,remainder", [
    ("next march 5th", (2018, 3, 5), ""),
    ("remind me next march 5th to pay", (2018, 3, 5), "remind me to pay"),
    ("this march 5th", (2018, 3, 5), ""),
    ("next january 10", (2018, 1, 10), ""),
    ("next march 5", (2018, 3, 5), ""),
    ("last march 5", (2017, 3, 5), ""),
    ("last january 10th", (2017, 1, 10), ""),
])
def test_relative_month_keeps_its_day(text, date, remainder):
    # The day after a marked month is part of the date.  "next" and "this"
    # take the next 5 March, 2018; "last" takes the latest one that has
    # passed, 5 March 2017.
    r = _span(text, "en")
    start = AstroDate(*date)
    assert r.span.start == start
    assert r.span.end == start + timedelta(days=1)
    assert r.remainder == remainder


@pytest.mark.parametrize("text,lang,date", [
    ("5 march next year", "en", (2018, 3, 5)),
    ("напомни 5 марта следующего года", "ru", (2018, 3, 5)),
    ("am 5. März nächsten Jahres", "de", (2018, 3, 5)),
    ("5 marca przyszłego roku", "pl", (2018, 3, 5)),
    ("5 марта этого года", "ru", (2017, 3, 5)),
    ("5 березня цього року", "uk", (2017, 3, 5)),
    ("5 марта прошлого года", "ru", (2016, 3, 5)),
    ("5 march last year", "en", (2016, 3, 5)),
])
def test_a_day_before_the_month_keeps_the_year_phrase(text, lang, date):
    """The day before the month is part of the date the year phrase places:
    "5 march next year" is 5 March 2018, said on 27 June 2017."""
    r = _span(text, lang)
    start = AstroDate(*date)
    assert (r.span.start, r.span.end) == (start, start + timedelta(days=1))
    assert "5" not in r.remainder


@pytest.mark.parametrize("text,lang,start", [
    ("since january", "en", datetime(2017, 1, 1)),
    ("I have been here since january", "en", datetime(2017, 1, 1)),
    ("с января", "ru", datetime(2017, 1, 1)),
    ("since july", "en", datetime(2016, 7, 1)),
])
def test_a_bare_month_after_since_has_begun(text, lang, start):
    """After "since" a bare month names the latest one that has begun, in
    every reader: January 2017 and July 2016, said on 27 June 2017."""
    assert _span(text, lang).span.start == start
    mentions = extract_timespans(text, lang, ANCHOR)
    assert [m.span.start for m in mentions] == [start]


@pytest.mark.parametrize("text,lang", [
    # a postposition follows the month.  hu "óta" is "since (a point in
    # time)" (en.wiktionary "óta"), hi "से" is "since/from" (en.wiktionary
    # "से", "कल से" = "since yesterday")
    ("január óta", "hu"),
    ("januárban óta", "hu"),
    ("जनवरी से", "hi"),
])
def test_a_bare_month_before_a_since_postposition_has_begun(text, lang):
    """The month names January 2017, said on 27 June 2017, in both readers."""
    assert _span(text, lang).span.start == datetime(2017, 1, 1)
    mentions = extract_timespans(text, lang, ANCHOR)
    assert [(m.span.start, m.span.end) for m in mentions] == [
        (datetime(2017, 1, 1), datetime(2017, 2, 1))]


def test_a_postposition_before_until_opens_a_range():
    """hi "से" is also "from": in "मार्च से जून तक" ("from March to June")
    the month is the start of a range, so it keeps its next occurrence."""
    mentions = extract_timespans("मार्च से जून तक", "hi", ANCHOR)
    assert (mentions[0].span.start, mentions[0].span.end) == (
        datetime(2018, 3, 1), datetime(2018, 4, 1))


@pytest.mark.parametrize("text, anchor, months", [
    ("जनवरी से मार्च तक", datetime(2026, 1, 30, 10), [(2026, 1), (2026, 3)]),
    ("मार्च से जून तक", datetime(2026, 1, 30, 10), [(2026, 3), (2026, 6)]),
    ("मैं जनवरी से मार्च तक यहाँ था", datetime(2026, 1, 30, 10),
     [(2026, 1), (2026, 3)]),
    ("जनवरी से मार्च तक", ANCHOR, [(2018, 1), (2018, 3)]),
])
def test_the_month_before_a_postposed_until_is_ahead(text, anchor, months):
    """hi "तक" is "until" (en.wiktionary "तक": "नौ बजे से दो बजे तक", "from
    nine o'clock up to two o'clock").  In "जनवरी से मार्च तक" the "से" is the
    postposition of January, so March is not read after "since": it is the
    next March, in the same year as the start."""
    mentions = extract_timespans(text, "hi", anchor)
    assert [(m.span.start.year, m.span.start.month) for m in mentions] == months


# Tuesday 27 June 2017: the next Monday is 3 July and its Friday 7 July; the
# Wednesday ahead is 28 June
_NEXT_MONDAY = ANCHOR.date() + timedelta(days=(0 - ANCHOR.weekday()) % 7)
_WEEK = (datetime.combine(_NEXT_MONDAY, datetime.min.time()),
         datetime.combine(_NEXT_MONDAY + timedelta(days=5), datetime.min.time()))


@pytest.mark.parametrize("text, lang, start, end", [
    ("we stay home since the office is closed from monday to friday", "en",
     *_WEEK),
    ("I am off since it is a holiday from monday until friday", "en", *_WEEK),
    ("the meeting moves since tuesday is a holiday from wednesday to friday",
     "en", datetime(2017, 6, 28), datetime(2017, 7, 1)),
    ("book the room since the hall is busy from 2 pm until 5 pm", "en",
     datetime(2017, 6, 27, 14), datetime(2017, 6, 27, 17, 1)),
    ("nous restons à la maison depuis que le bureau est fermé du lundi au "
     "vendredi", "fr", *_WEEK),
    ("ficamos em casa desde que o escritório está fechado de segunda a sexta",
     "pt", *_WEEK),
    ("wir bleiben zu hause seit das büro von montag bis freitag geschlossen "
     "ist", "de", *_WEEK),
])
def test_a_since_of_cause_leaves_the_range_ahead(text, lang, start, end):
    """In mid-sentence "since" may be the conjunction "because" (en.wiktionary
    "since", conjunction: "Since you didn't call, we left without you.").
    Then it does not govern a date, and the range after it stays ahead, in
    both readers.  fr "depuis que", pt "desde que" and de "seit" before a
    clause read the same."""
    r = _span(text, lang)
    assert (r.span.start, r.span.end) == (start, end)
    assert extract_timespans(text, lang, ANCHOR)[-1].span.start.date() \
        == start.date()


@pytest.mark.parametrize("text, left", [
    ("since january until march", ""),
    ("since january to march", ""),
    ("I have lived here since january until march", "I have lived here"),
])
def test_a_range_after_since_has_begun(text, left):
    """"since january until march" said on 27 June 2017 is January to March
    2017 in both readers: the speaker says the range has begun."""
    r = _span(text, "en")
    assert (r.span.start, r.span.end) == (datetime(2017, 1, 1),
                                          datetime(2017, 4, 1))
    assert r.remainder == left
    mentions = extract_timespans(text, "en", ANCHOR)
    assert [(m.span.start, m.span.end) for m in mentions] == [
        (datetime(2017, 1, 1), datetime(2017, 4, 1))]


def test_an_until_in_a_later_sentence_leaves_since_january_begun():
    """Only an "until" right after the month closes a range on it.  In "I have
    been here since january. I stay until friday" the month after "since" is
    January 2017, and the Friday is 30 June 2017."""
    mentions = extract_timespans(
        "I have been here since january. I stay until friday", "en", ANCHOR)
    assert [(m.span.start, m.span.end) for m in mentions] == [
        (datetime(2017, 1, 1), datetime(2017, 2, 1)),
        (datetime(2017, 6, 30), datetime(2017, 7, 1))]
