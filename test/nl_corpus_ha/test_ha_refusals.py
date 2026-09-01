"""Every construction this locale declines, pinned so the absence is a
property of the suite rather than an oversight.
"""
import pytest

from ._corpus import day, nomatch, start_end


@pytest.mark.parametrize("text", ["bara", "bana", "badi"])
def test_the_one_word_year_deictics_are_not_read(text):
    """CLDR gives Hausa a single word for last, this and next year.

    They are real and well attested -- en.wiktionary.org has lemma entries
    for bara and bana -- but this library has no construction for a year
    deixis carried by one word with no unit noun beside it, and inventing
    one is a change to the engine rather than to a locale.  The phrasal
    forms answer instead: "shekarar da ta gabata", "wannan shekarar",
    "shekara mai zuwa".
    """
    nomatch(text)


@pytest.mark.parametrize("text", ["jibi", "gata"])
def test_no_day_after_tomorrow_word_ships(text):
    """CLDR carries no relative-type-2 for Hausa and no source consulted
    attests a day-after-tomorrow word, so none ships.  The day-BEFORE-
    yesterday counterpart does: shekaranjiya is glossed in two Chadic
    comparative wordlists on ha.wikipedia.org."""
    nomatch(text)


def test_the_day_before_yesterday_still_reads():
    assert start_end("shekaranjiya") == day(2027, 5, 10)


@pytest.mark.parametrize("text", ["kaka", "damina", "rani"])
def test_no_season_vocabulary_ships(text):
    """The Hausa year is divided by the rains, not by four temperate seasons,
    and no source consulted states boundaries for any of these words.
    Boundaries nobody stated are not invented."""
    nomatch(text)


@pytest.mark.parametrize("text", ["kwata", "kwata na gaba", "wannan kwatan"])
def test_the_quarter_is_not_read(text):
    """CLDR gives Hausa a quarter field, but its forms are phrases with an
    internal genitive ("kwata na gaba") and this library's quarter
    constructions are built on a single quarter noun."""
    nomatch(text)


@pytest.mark.parametrize("text", ["ƙarni", "ƙarni na ashirin", "shekaru goma"])
def test_no_century_or_decade_scope_unit_ships(text):
    """CLDR's Hausa units are exactly the seven it counts -- second, minute,
    hour, day, week, month, year.  ƙarni is a real noun for a century, but
    nothing consulted shows it counted or ordinal-scoped in running text,
    and this library's scope units are read from usage rather than derived.
    """
    nomatch(text)


@pytest.mark.parametrize("text", ["Li", "Ta", "Lr", "Al", "Ju", "As", "Lh"])
def test_the_two_letter_weekday_forms_are_not_read(text):
    """CLDR's days.format.short series is seven ordinary letter pairs, and
    Ta collides with the feminine genitive linker.  The three-letter
    abbreviations ship instead, and only beside a marker."""
    nomatch(text)


@pytest.mark.parametrize("text", ["awa daya da rabi", "rabi", "awa da rabi"])
def test_the_fractional_phrase_is_not_a_span(text):
    """"awa daya da rabi" (an hour and a half) is attested on
    ha.wikipedia.org, but it names how long something lasts, not a point or
    range on the calendar, so ``extract_timespan`` has nothing to claim here
    even though ``extract_duration`` reads the same words (see
    test_ha_duration.py)."""
    nomatch(text)


@pytest.mark.parametrize("text", ["Sallah", "Kirsimeti", "Ranar Samun 'Yanci"])
def test_no_holiday_vocabulary_ships(text):
    """No holiday names ship for this locale; the dates behind them are a
    jurisdiction question, not a vocabulary one."""
    nomatch(text)


@pytest.mark.xfail(
    reason="zuwa closes a range and the range split reads the raw token "
           "stream before multiword surfaces are merged, so the coming-"
           "weekday form is claimed by the open range 'up to Monday'",
    strict=True)
def test_the_coming_weekday_form_is_shadowed_by_the_range_terminator():
    """CLDR's relative-type-1 for a weekday is "Litinin mai zuwa".

    The unit forms of the same marker work -- "wata mai zuwa" is next month
    and "sati mai zuwa" is next week -- but a weekday leaves the phrase open
    to the range reading, and the range pass runs first.  This test states
    what the phrase means; it will start passing when the two can be told
    apart.
    """
    assert start_end("Litinin mai zuwa") == day(2027, 5, 17)
