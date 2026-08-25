"""What this locale deliberately does not read, and why.

Each pin below records a surface that was considered and left out.  They are
tests rather than a comment so that adding the surface later has to change a
stated decision, and so that nothing here can quietly start returning a
confident answer built on an unsourced guess.
"""
import pytest

from chronologia.extract.numfold_filipino import read_spanish_run

from ._corpus import nomatch, remainder, span, start


@pytest.mark.parametrize("text", ["alas una", "ala una"])
def test_una_is_not_folded_to_one(text):
    """``una`` is glossed as the adjective "first", not as a numeral, and it
    is far too ordinary a word to read as 1 on that basis.  The hour one is
    ``ala uno``, whose numeral sense is attested."""
    nomatch(text)


def test_the_attested_spelling_of_hour_one_does_work():
    assert start("ala uno").hour == 1


@pytest.mark.parametrize("text", ["ika-dalawa ng Hulyo 2020",
                                  "ika-tatlo ng Hulyo 2020"])
def test_the_separated_second_and_third_ordinals_are_not_read(text):
    """The attested second and third are the suppletive ``ikalawa`` and
    ``ikatlo``; ``ika-dalawa`` and ``ika-tatlo`` are formed by analogy and
    attested nowhere, so the fold leaves the prefix standing."""
    assert "ika" in remainder(text)


@pytest.mark.parametrize("text,d", [("ikalawa ng Hulyo 2020", 2),
                                    ("ikatlo ng Hulyo 2020", 3)])
def test_the_attested_second_and_third_do_work(text, d):
    assert start(text).day == d


@pytest.mark.parametrize("word", ["sesenta", "nobenta"])
def test_sixty_and_ninety_are_not_shipped_in_the_spanish_set(word):
    """Their dictionary entries carry only a money noun ("sixty pesos") and
    no numeral sense, so neither is folded.  Neither is reachable from the
    clock anyway -- minutes stop at fifty-nine, and ``singkuwenta`` covers
    that."""
    assert read_spanish_run((word,)) is None
    assert read_spanish_run(("singkuwenta", "y", "nuwebe")) == 59


@pytest.mark.parametrize("text", [
    "madaling-araw", "sa madaling-araw",
])
def test_madaling_araw_is_not_a_daypart_here(text):
    """CLDR fil labels its 06:00-12:00 band ``madaling-araw`` and its
    00:00-06:00 band ``umaga``, the reverse of the two words' dictionary
    senses -- ``madaling-araw`` is glossed as the period between midnight and
    sunrise.  Which band the word names is therefore unresolved, and no band
    is bound to it."""
    nomatch(text)


def test_the_evening_band_ships_no_surface():
    """CLDR fil gives ``gabi`` for both its evening band (16:00-18:00) and
    its night band (18:00-24:00).  The word is bound to night, the wider of
    the two; binding it to both would make the deictic ambiguous, and there
    is no second word to give the narrower band."""
    from ._corpus import start_end
    s, e = start_end("gabi")
    assert (s.hour, e.hour) == (18, 0)


@pytest.mark.parametrize("abbrev,month", [
    ("ene", 1), ("peb", 2), ("mar", 3), ("abr", 4), ("may", 5), ("hun", 6),
    ("hul", 7), ("ago", 8), ("set", 9), ("okt", 10), ("nob", 11),
    ("dis", 12),
])
def test_month_abbreviations_are_not_shipped(abbrev, month):
    """Every CLDR fil month abbreviation is either a live Tagalog word or a
    rival abbreviation: ``may`` is the existential "there is", ``mar``
    abbreviates both Marso and Martes.  Only the wide names ship, so an
    abbreviation reads as the bare year and leaves itself unconsumed."""
    s = span(f"{abbrev} 2021")
    assert (s.start.year, s.start.month, s.start.day) == (2021, 1, 1)
    assert abbrev in remainder(f"{abbrev} 2021")


@pytest.mark.parametrize("text", ["araw-araw", "buwan-buwan", "taon-taon"])
def test_reduplicated_recurrence_is_not_shipped(text):
    """Filipino has two "every X" mechanisms, the particle ``tuwing`` and
    reduplication of the unit noun.  Only the particle ships: the
    reduplicated forms are a closed set of derived adverbs rather than a
    marker, ``linggo-linggo`` has no dictionary entry at all, and nothing
    sources whether the two mechanisms are interchangeable."""
    nomatch(text)


def test_the_reduplicated_week_is_not_read_as_a_recurrence():
    """``linggo-linggo`` is two Sunday surfaces to this locale, so one of
    them is left unconsumed rather than the pair reading as "every week"."""
    assert "linggo" in remainder("linggo-linggo")


@pytest.mark.parametrize("text", ["tagsibol", "taglagas", "taglamig",
                                  "tag-init", "tag-ulan"])
def test_seasons_are_not_shipped(text):
    """The Philippines has a dry and a wet season, ``tag-init`` and
    ``tag-ulan``, which are not the four temperate seasons chronologia's
    season slot models; the four temperate words exist as translations but
    name no local period.  Mapping one set onto the other would invent a
    calendar."""
    nomatch(text)


def test_the_quarter_hour_has_no_dedicated_word():
    """The half is ``medya``; nothing sources a quarter lexeme beside it, and
    the worked 3:45 example spells the minutes out ("kuwarenta singko")
    rather than using one."""
    assert start("alas tres y kuwarto").hour == 3
    assert "kuwarto" in remainder("alas tres y kuwarto")
