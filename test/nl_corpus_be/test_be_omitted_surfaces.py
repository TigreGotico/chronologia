"""What this locale deliberately does not read, pinned so it stays honest.

Each phrase below names something Belarusian genuinely says but that this
locale refuses: either the wording is unsourced, or the engine has no slot
shape that could carry it without inventing an answer.  The contract is
refusal -- nothing returned, or the unread word left in the remainder --
rather than a plausible guess.  Each pin becomes a failing test the day the
gap is closed, which is exactly when the behaviour should be revisited.
"""
import pytest

from ._corpus import nomatch, parse


@pytest.mark.parametrize("text", ["залетась", "пазалетась"])
def test_the_two_years_back_deictics(text):
    """Wiktionary lists залетась and пазалетась as derived terms of летась,
    both glossed "two years ago", which is one gloss for two distinct words --
    the pair cannot both name the same year, and no source consulted separates
    them.  летась and сёлета, which CLDR fixes exactly, do read."""
    nomatch(text)


@pytest.mark.parametrize("text", ["у гэту гадзіну", "гэтая гадзіна"])
def test_no_relative_hour_period(text):
    """CLDR gives "у гэту гадзіну" as the hour field's relative-type-0, but the
    resolver has no sub-day relative period at all -- English "this hour" is
    refused by the same engine path.  Not a gap in this locale, and not one to
    paper over here."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "пяць хвілін на трэцюю", "дзесяць хвілін на першую",
    "дваццаць хвілін на восьмую",
])
def test_a_minute_count_in_the_first_half_of_the_hour(text):
    """Вячорка's first-half rule covers a spelled minute count as well as a
    fraction ("пяць хвілін на трэцюю" == 02:05).  The clock resolver has no
    additive toward-hour branch for a numeric minute -- its only toward-hour
    path is the fixed fraction, and its only numeric-minute path subtracts --
    so this reading would come out as 03:00, an hour and five minutes wrong.
    Refused until the engine can carry it; the fraction forms of the same
    idiom ("палова на трэцюю", "чвэрць на трэцюю") do ship."""
    nomatch(text)


def test_the_fraction_form_of_the_first_half_does_read():
    """The control for the pin above."""
    s = parse("палова на трэцюю")[0].start
    assert (s.hour, s.minute) == (2, 30)


@pytest.mark.parametrize("text", [
    "другая гадзіна пяць хвілін", "шаснаццатая гадзіна трыццаць хвілін",
])
def test_the_official_hour_plus_minutes_register(text):
    """The announcement register spells the hour as an ordinal and the
    minutes as a bare cardinal after it.  No construction order binds a
    trailing minute count onto an hour, so the minutes would be silently
    dropped and the hour returned on the dot.  The digit form of the same
    time (16:30) is what reads."""
    r = parse(text)
    assert r is None or "хвілін" in r[1]


@pytest.mark.parametrize("text", ["чвэрць да шостай", "квадранец да шостай"])
def test_the_da_form_of_the_subtractive_clock(text):
    """Вячорка lists да alongside без and за for the second half of the hour.
    да is also the ordinary preposition for every range end and deadline in
    the language ("да пяці гадзін", "з 5 да 12 ліпеня"), and reading it as a
    clock direction would turn those into clock times.  The без and за forms
    of the same reading ship instead."""
    nomatch(text)


@pytest.mark.parametrize("text,h,mi", [
    ("без чвэрці шостая", 5, 45), ("за чвэрць шостая", 5, 45),
])
def test_the_bez_and_za_forms_do_read(text, h, mi):
    """The control for the pin above."""
    s = parse(text)[0].start
    assert (s.hour, s.minute) == (h, mi)


@pytest.mark.parametrize("text", [
    "раніцай", "удзень", "вечарам", "ноччу", "сёння раніцай", "заўтра вечарам",
])
def test_no_daypart_bands(text):
    """CLDR has no ``dayPeriodRuleSet`` entry for be -- the boundary hours
    that would turn раніца into a clock band were never defined for this
    language.  Inventing them is the thing this pin prevents, so the four
    daypart words ship no band and a bare daypart names no time.  The deictic
    day in front of one still resolves, with the daypart left unread."""
    r = parse(text)
    assert r is None or "раніцай" in r[1] or "вечарам" in r[1]


@pytest.mark.parametrize("text", [
    "5 стагоддзяў таму", "праз 10 стагоддзяў", "тысячагоддзе",
    "2 тысячагоддзі таму",
])
def test_no_century_or_millennium_counts(text):
    """CLDR's field set carries no relativeTime patterns for the century or
    the millennium in be, so their plural forms are unsourced and are not
    shipped.  The ordinal century, which is sourced as an ordinary neuter
    noun, does read."""
    nomatch(text)


def test_the_ordinal_century_does_read():
    """The control for the pin above."""
    s, e = parse("20-е стагоддзе")[0].start, parse("20-е стагоддзе")[0].end
    assert (s.year, e.year) == (1900, 2000)


@pytest.mark.parametrize("text", [
    "сто дваццаць першага студзеня", "сто дваццаць першы квартал",
])
def test_no_compound_ordinals_past_a_hundred(text):
    """The numeral module tabulates compound ordinals only through 100; the
    pattern past it was not separately verified, so it is not extrapolated."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "праз 5 мінут", "5 мінут таму", "праз 2 часы", "у понедельник",
    "завтра", "вчера", "послезавтра",
])
def test_russian_wording_is_not_read_as_belarusian(text):
    """The closest sibling language, and the one this locale would have been
    silently wrong in if it had been bootstrapped by translating."""
    r = parse(text)
    assert r is None or r[0].start.date().year == 2017 and r[1] != ""
