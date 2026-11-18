# -*- coding: utf-8 -*-
"""Portuguese spelled numbers that numtag reads whole.

A spelled year with "mil" ("dois mil e vinte e seis") and a count with a
collective noun ("duas dúzias") are one number each.  A deep-time age is the
whole number before "anos", in the scale of the language tag: pt-PT counts
the long scale and pt-BR the short scale (Priberam, "bilião", senses 1 and
2).  Every expected value is
written by hand or computed with ``relativedelta`` from the anchor.
"""
import pytest

from chronologia import extract_duration, extract_timespan, extract_timespans
from chronologia.events import extract_event

from ._corpus import (ANCHOR, AstroDate, datetime, nomatch, parse,
                      relativedelta, span, timedelta)


@pytest.mark.parametrize("text,year", [
    ("em dois mil e vinte e seis", 2026),
    ("no ano de dois mil e vinte e seis", 2026),
    ("em mil novecentos e noventa e nove", 1999),
    ("no ano mil e quinhentos", 1500),
])
def test_spelled_year_with_mil(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    text = "vinte e cinco de dezembro de dois mil e vinte e cinco"
    s = span(text)
    assert (s.start, s.end) == (datetime(2025, 12, 25), datetime(2025, 12, 26))
    assert parse(text).remainder == ""


def test_spelled_year_and_clock_half():
    text = "a 3 de março de dois mil e três às duas e meia"
    assert span(text).start == datetime(2003, 3, 3, 2, 30)
    assert parse(text).remainder == ""


def test_collective_noun_count():
    """Duas dúzias is 2 x 12 = 24 years."""
    text = "há duas dúzias de anos"
    assert span(text).start == ANCHOR - relativedelta(years=24)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,days", [
    ("há meia dúzia de dias", 6),           # 12 / 2
    ("há uma dúzia e meia de dias", 18),    # 12 + 12 / 2
])
def test_half_inside_a_count(text, days):
    assert span(text).start == ANCHOR - timedelta(days=days)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,lang,years,width", [
    # 1 000 000 + 200 000, said to the thousand
    ("há um milhão e duzentos mil anos", "pt", 1_200_000, 1_000),
    # 2 000 000 + 300 000, said to the thousand
    ("há dois milhões e trezentos mil anos", "pt", 2_300_000, 1_000),
    ("há dois milhões e quinhentos mil anos", "pt", 2_500_000, 1_000),
    # 1 000 000 / 2, said to a tenth of a million
    ("há meio milhão de anos", "pt", 500_000, 100_000),
    # 2 * 10^6 + 10^6 / 2 and 10^6 + 10^6 / 2, said to a tenth of a million
    ("há dois milhões e meio de anos", "pt", 2_500_000, 100_000),
    ("há um milhão e meio de anos", "pt", 1_500_000, 100_000),
    # pt-PT: 1000 * 10^6 + 1000 * 10^6 / 2 = 1500 milhões, said to the million
    ("há mil milhões e meio de anos", "pt", 1_500_000_000, 1_000_000),
    # pt-BR: 2 * 10^9 + 10^9 / 2, said to a tenth of a billion
    ("há dois bilhões e meio de anos", "pt-BR", 2_500_000_000, 100_000_000),
    # pt-BR: bilhão = 10^9, so 2*10^9 + 500*10^6, said to the million
    ("há dois bilhões e quinhentos milhões de anos", "pt-BR",
     2_500_000_000, 1_000_000),
    ("há um bilhão e duzentos milhões de anos", "pt-BR",
     1_200_000_000, 1_000_000),
    # pt-PT: bilhão and bilião = 10^12, so 2*10^12 + 500*10^6
    ("há dois bilhões e quinhentos milhões de anos", "pt",
     2_000_500_000_000, 1_000_000),
    # pt-PT: 2*10^12 + 500*10^3*10^6
    ("há dois biliões e quinhentos mil milhões de anos", "pt",
     2_500_000_000_000, 1_000_000),
])
def test_deep_time_count_with_several_scale_words(text, lang, years, width):
    """The start year is 1950 - years before present, and the span is one
    unit of the last digit said wide."""
    got = extract_timespan(text, lang, ANCHOR)
    assert (got.span.start, got.span.end) == (
        AstroDate(1950 - years, 1, 1), AstroDate(1950 - years + width, 1, 1))
    assert got.remainder == ""


def test_scale_count_of_seconds_is_no_year():
    """"dois mil milhões" is 2 x 1000 x 10^6 = 2*10^9 seconds."""
    text = "daqui a dois mil milhões de segundos"
    assert span(text).start == ANCHOR + timedelta(seconds=2_000_000_000)
    assert extract_duration(text, "pt").duration == timedelta(
        seconds=2_000_000_000)


def test_scale_count_of_things_is_no_year():
    nomatch("comprei dois mil milhões de livros")


_YESTERDAY = (datetime(2017, 6, 26), datetime(2017, 6, 27))
_TOMORROW = (datetime(2017, 6, 28), datetime(2017, 6, 29))


@pytest.mark.parametrize("lang, text, day", [
    # a scale word before a noun counts things: no year 1000 or 2000
    ("pt", "comprei mil ações ontem", _YESTERDAY),
    ("pt", "vi mil pessoas ontem", _YESTERDAY),
    ("pt", "vendi duas mil ações ontem", _YESTERDAY),
    ("en", "I saw a thousand people yesterday", _YESTERDAY),
    ("en", "a thousand people came tomorrow", _TOMORROW),
])
def test_a_count_of_things_leaves_the_day_word_the_date(lang, text, day):
    s = extract_timespan(text, lang, ANCHOR).span
    assert (s.start, s.end) == day


_MONDAY = ANCHOR.date() + relativedelta(weekday=0, days=1)
_MONDAY = (datetime.combine(_MONDAY, datetime.min.time()),
           datetime.combine(_MONDAY + timedelta(days=1), datetime.min.time()))
_TODAY = (datetime(2017, 6, 27), datetime(2017, 6, 28))


@pytest.mark.parametrize("lang, text, day", [
    # more number words after the scale word: still a count, not a year
    ("pt", "ganhei dois mil e quinhentos euros amanhã", _TOMORROW),
    ("pt", "paguei mil e duzentos euros na segunda", _MONDAY),
    ("pt", "comprei mil e duzentas ações ontem", _YESTERDAY),
    ("pt", "vi três mil e cem pessoas ontem", _YESTERDAY),
    # a number before a day word, with no year cue before it, is no year
    ("pt", "paguei mil na segunda", _MONDAY),
    ("pt", "gastei mil hoje", _TODAY),
    ("pt", "comprei mil, ontem", _YESTERDAY),
    ("en", "I paid a thousand on monday", _MONDAY),
    ("en", "I saw two thousand five hundred people yesterday", _YESTERDAY),
])
def test_a_count_with_more_number_words_leaves_the_day_word_the_date(
        lang, text, day):
    s = extract_timespan(text, lang, ANCHOR).span
    assert (s.start, s.end) == day


def test_desde_cues_a_spelled_year_with_a_clause_after_it():
    """"desde 2010 vivo aqui" runs from the start of 2010 to the anchor, and
    the spelled year reads the same."""
    s, rest = parse("desde dois mil e dez vivo aqui")
    assert (s.start, s.end) == (datetime(2010, 1, 1), ANCHOR)
    assert rest == "vivo aqui"


#: Friday 30 January 2026, 10:00.
_FRIDAY = datetime(2026, 1, 30, 10, 0)
_THURSDAY_29 = (datetime(2026, 1, 29), datetime(2026, 1, 30))
_MONDAY_2 = (datetime(2026, 2, 2), datetime(2026, 2, 3))


def _event_day(lang, text):
    s = extract_event(text, lang, anchor=_FRIDAY).span
    return s.start, s.end


@pytest.mark.parametrize("lang, text, day", [
    ("pt", "paguei até dois mil euros na segunda", _MONDAY_2),
    ("pt", "gastei até três mil euros ontem", _THURSDAY_29),
    ("en", "we paid until three thousand dollars on monday", _MONDAY_2),
])
def test_a_currency_after_a_cued_number_makes_it_an_amount(lang, text, day):
    """A currency after the number makes it an amount, also after a range
    word: the day word is the date."""
    assert _event_day(lang, text) == day


@pytest.mark.parametrize("text", [
    "até dois mil euros",
    "até cinco mil pessoas",
    "a partir de três mil euros por mês",
    "entre mil e dois mil euros",
])
def test_an_amount_after_ate_a_partir_de_or_entre_is_no_year(text):
    """"até", "a partir de" and "entre" are no year cue: in pt they mostly
    put an amount after them."""
    nomatch(text)


@pytest.mark.parametrize("lang, text, day", [
    ("pt", "esperei até. Dois mil turistas chegaram ontem", _THURSDAY_29),
    ("pt", "esperei desde, dois mil turistas chegaram ontem", _THURSDAY_29),
    ("en", "I left after. Two thousand people came yesterday", _THURSDAY_29),
    ("en", "the shop opened since; two thousand people came yesterday",
     _THURSDAY_29),
    ("en", "we waited until. Three thousand tickets sold on monday",
     _MONDAY_2),
])
def test_a_cue_in_the_clause_before_is_no_cue(lang, text, day):
    assert _event_day(lang, text) == day


@pytest.mark.parametrize("lang, text, years, rest", [
    ("en", "from two thousand to two thousand and ten it rained",
     (2000, 2011), "it rained"),
    ("en", "between two thousand and two thousand and five it rained",
     (2000, 2006), "it rained"),
    ("pt", "desde dois mil até dois mil e dez choveu", (2000, 2011),
     "choveu"),
])
def test_the_second_endpoint_of_a_range_reads_the_cue_of_the_first(
        lang, text, years, rest):
    s, left = extract_timespan(text, lang, _FRIDAY)
    assert (s.start, s.end, left) == (datetime(years[0], 1, 1),
                                      datetime(years[1], 1, 1), rest)


@pytest.mark.parametrize("lang, text", [
    ("en", "between two thousand and three thousand dollars"),
    ("en", "from two thousand to three thousand euros"),
    ("en", "from one thousand to two thousand dollars"),
    ("pt", "desde dois mil até três mil euros"),
])
def test_a_currency_after_the_second_number_of_a_range_measures_both(
        lang, text):
    """A currency after the second number of a range makes the first number
    an amount too, so the range holds no year."""
    assert extract_timespans(text, lang, _FRIDAY) == []


@pytest.mark.parametrize("lang, text, day", [
    ("en", "we paid between two thousand and three thousand dollars on monday",
     _MONDAY_2),
    ("en", "between two thousand and three thousand dollars were stolen "
     "yesterday", _THURSDAY_29),
    ("pt", "pagámos desde dois mil até três mil euros na segunda", _MONDAY_2),
])
def test_a_range_of_amounts_leaves_the_day_word_as_the_date(lang, text, day):
    assert _event_day(lang, text) == day


def test_a_currency_in_the_next_sentence_measures_no_number():
    """A full stop ends the range: "Dollars" starts the next sentence."""
    s, left = extract_timespan(
        "from two thousand to two thousand and ten. Dollars were spent",
        "en", _FRIDAY)
    assert (s.start, s.end, left) == (datetime(2000, 1, 1),
                                      datetime(2011, 1, 1),
                                      "Dollars were spent")


@pytest.mark.parametrize("lang, text, length, rest", [
    ("en", "between two thousand and three thousand days",
     timedelta(days=3000), "between two thousand and"),
    ("en", "between two thousand and three thousand hours",
     timedelta(hours=3000), "between two thousand and"),
    ("pt", "entre dois mil e três mil dias", timedelta(days=3000),
     "entre dois mil e"),
])
def test_a_range_of_time_units_holds_no_year_and_adds_no_thousand(
        lang, text, length, rest):
    """The first number of a range of units folds into a number, so the
    duration reader takes the second number alone, as on origin/dev, and no
    "thousand" of the first number adds to it."""
    assert extract_timespans(text, lang, _FRIDAY) == []
    found = extract_duration(text, lang, anchor=_FRIDAY)
    assert (found.duration, found.remainder) == (length, rest)


@pytest.mark.parametrize("lang, text, day", [
    ("pt", "pagámos entre dois mil e três mil euros na segunda", _MONDAY_2),
    ("pt", "vieram entre dois mil e três mil turistas ontem", _THURSDAY_29),
    ("pt-BR", "pagamos entre dois mil e três mil reais na segunda",
     _MONDAY_2),
])
def test_an_entre_range_of_counts_leaves_the_day_word_as_the_date(
        lang, text, day):
    """"entre" is no year cue, and a word comes after the range, so both
    numbers count things, also when the range reader folds the first one
    alone."""
    s = extract_timespan(text, lang, _FRIDAY).span
    assert (s.start, s.end) == day


@pytest.mark.parametrize("lang, text", [
    ("en", "since two thousand only three thousand dollars were spent"),
    ("pt", "desde dois mil só três mil euros foram gastos"),
])
def test_a_word_that_closes_no_range_lets_no_unit_reach_the_first_number(
        lang, text):
    """Only the word that closes the cue ("until", "até") makes a range:
    after "only" or "só" the currency measures the second number alone, and
    the first number stays a year."""
    s = extract_timespan(text, lang, _FRIDAY).span
    assert (s.start, s.end) == (datetime(2000, 1, 1), _FRIDAY)


def test_known_cost_a_year_after_ate():
    """Known cost: "até" is no year cue, so the year 2030 reads as a count,
    as on origin/dev."""
    assert extract_timespan("até dois mil e trinta vamos poupar", "pt",
                            _FRIDAY) is None


@pytest.mark.parametrize("lang, text, span_", [
    ("en", "before three thousand fans arrived yesterday",
     (datetime(3000, 1, 1), datetime(3001, 1, 1))),
    ("pt", "desde dois mil turistas chegaram ontem",
     (datetime(2000, 1, 1), _FRIDAY)),
])
def test_known_cost_a_count_of_people_after_a_cue(lang, text, span_):
    """Known cost: only a unit or a currency after the number makes it a
    count after a cue.  A noun such as "fans" or "turistas" does not, so the
    number reads as a year.  origin/dev reads the en row the same."""
    s = extract_timespan(text, lang, _FRIDAY).span
    assert (s.start, s.end) == span_


@pytest.mark.parametrize("text", [
    "uma multidão de dois mil chegou",
    # Known cost: "de" also takes a count ("uma multidão de dois mil"), so it
    # is no year cue, and the census year 2011 reads as a count.
    "o censo de dois mil e onze mostrou",
])
def test_a_spelled_number_after_de_with_a_word_after_it_is_a_count(text):
    nomatch(text)


@pytest.mark.parametrize("lang, text", [
    ("pt", "dois mil e quinhentos euros"),
    ("pt", "mil, dois dias"),
    ("en", "two thousand and one hundred thousand"),
    # a scale word with no number before it names no year
    ("pt", "mil"),
    ("pt", "paguei mil"),
])
def test_a_count_before_a_noun_or_a_number_is_no_year(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None
    assert extract_timespans(text, lang, ANCHOR) == []
    assert extract_event(text, lang, anchor=ANCHOR) is None


@pytest.mark.parametrize("lang, text, length", [
    ("pt", "mil e quinhentas horas", timedelta(hours=1500)),
    ("en", "two thousand five hundred minutes", timedelta(minutes=2500)),
    ("en", "one thousand five hundred hours", timedelta(hours=1500)),
])
def test_a_count_before_a_unit_is_a_length_and_no_year_or_clock(
        lang, text, length):
    """"quinhentas" is the feminine form, so a year is never spelled with
    it (en.wiktionary "quinhentas"); "hours" after "one thousand five
    hundred" counts hours, and the clock says "fifteen hundred hours"."""
    assert extract_timespans(text, lang, ANCHOR) == []
    assert extract_duration(text, lang, anchor=ANCHOR).duration == length


@pytest.mark.parametrize("lang, text, year, month", [
    ("pt", "março de dois mil e três às três", 2003, 3),
    ("pt", "janeiro de mil novecentos e noventa e nove foi frio", 1999, 1),
    ("en", "in two thousand and one I saw people", 2001, 1),
])
def test_a_year_after_a_cue_or_a_month_stays_the_year(
        lang, text, year, month):
    s = extract_timespan(text, lang, ANCHOR).span
    assert (s.start.year, s.start.month) == (year, month)


@pytest.mark.parametrize("text, year", [
    # after a year cue, or with no word after it, the number is the year
    ("no ano mil", 1000),
    ("em dois mil eu nasci", 2000),
])
def test_a_scale_word_after_a_year_cue_stays_the_year(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))


@pytest.mark.parametrize("lang, text", [
    ("pt", "em MMXX"),
    ("en", "in MMXX"),
])
def test_a_bare_roman_numeral_after_a_connector_is_no_year(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text", [
    "há mil duzentos anos",
    "há dois milhões trezentos mil anos",
    "há mil duzentos milhões de anos",
])
def test_two_numbers_before_the_unit_give_no_count(text):
    """The standard form of 1200 is "mil e duzentos" (Cunha and Cintra,
    Nova Gramática do Português Contemporâneo, 1984, p. 372, quoted in
    Ciberdúvidas 34389; the Gulbenkian Gramática do Português, pp. 932-933,
    was not consulted).  numtag reads "mil duzentos" as 1000 and 200, so the
    count of years is not settled: no slot reads it, and "anos" does not
    read as one year."""
    nomatch(text)
    assert extract_timespans(text, "pt", ANCHOR) == []
    assert extract_duration(text, "pt", anchor=ANCHOR) is None


@pytest.mark.parametrize("text,expected,left", [
    ("o autocarro dez cinco minutos atrás", ANCHOR - timedelta(minutes=5),
     "o autocarro dez"),
    ("sala três dois dias atrás", ANCHOR - timedelta(days=2), "sala três"),
])
def test_a_number_that_names_a_thing_leaves_the_count_after_it(
        text, expected, left):
    """"dez" names the bus and "três" the room: neither ends in a scale
    word, so the number after it is the count."""
    got = parse(text)
    assert got.span.start == expected
    assert got.remainder == left


def test_mil_with_e_is_one_count():
    """"mil e duzentos" is 1000 + 200 = 1200.  "mil" has no count word
    before it, so it is no deep-time scale, and the phrase reads as its
    digits "há 1200 anos" do."""
    text = "há mil e duzentos anos"
    assert span(text).start == ANCHOR - relativedelta(years=1200)
    assert parse(text).remainder == ""


def test_a_comma_after_a_scale_word_ends_the_number():
    """A comma ends "mil", so "dois dias" is a count of its own."""
    got = extract_duration("mil, dois dias", "pt")
    assert got.duration == timedelta(days=2)
    assert got.remainder == "mil"


@pytest.mark.parametrize("lang, text", [
    ("en", "from two thousand to three thousand $"),
    ("en", "between two thousand and three thousand €"),
    ("en", "between two thousand and three thousand US$"),
    ("en", "between two thousand and three thousand USD"),
    ("en", "between two thousand and three thousand ALL"),
    ("en", "between two thousand and three thousand US dollars"),
    ("en", "between two thousand and three thousand more dollars"),
    ("pt", "desde dois mil até três mil €"),
    ("pt", "desde dois mil até três mil EUR"),
    ("pt", "desde dois mil até três mil mais euros"),
])
def test_a_currency_symbol_code_or_qualified_name_measures_a_range(
        lang, text):
    """A currency symbol, an ISO 4217 code or a currency name after one
    qualifying word makes both numbers of a range amounts (CLDR 49.0.0
    currency symbols, codes and display names such as "US dollars"); "more"
    and "mais" qualify the quantity (Wiktionary "more", Priberam "mais")."""
    assert extract_timespans(text, lang, _FRIDAY) == []


@pytest.mark.parametrize("lang, text, day", [
    ("en", "we paid between two thousand and three thousand USD on monday",
     _MONDAY_2),
    ("en", "between two thousand and three thousand $ were stolen yesterday",
     _THURSDAY_29),
])
def test_a_range_of_amounts_with_a_symbol_or_code_leaves_the_day_word(
        lang, text, day):
    assert _event_day(lang, text) == day


@pytest.mark.parametrize("text", [
    "between two thousand and three thousand all",
    "since two thousand try again",
])
def test_a_word_spelled_like_an_iso_code_in_lower_case_is_no_currency(text):
    """"all" and "try" are the codes ALL and TRY only in capitals."""
    s = extract_timespan(text, "en", _FRIDAY).span
    assert s.start == datetime(2000, 1, 1)


@pytest.mark.parametrize("lang, text, years", [
    ("en", "in two thousand the dollar rose", (2000, 2001)),
    ("en", "since two thousand the euro fell", (2000, None)),
    ("pt", "em dois mil o euro subiu", (2000, 2001)),
    ("pt", "desde dois mil o euro caiu", (2000, None)),
])
def test_an_article_between_a_year_and_a_currency_noun_is_no_qualifier(
        lang, text, years):
    """Only a word that qualifies a currency stands between a number and its
    currency noun, so the article of the next phrase keeps the number a
    year."""
    s = extract_timespan(text, lang, _FRIDAY).span
    assert s.start == datetime(years[0], 1, 1)
    assert years[1] is None or s.end == datetime(years[1], 1, 1)
