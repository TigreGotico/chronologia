"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Welsh surfaces could not be
attested, or whose sources disagreed, so no vocabulary ships for it.  The
contract is refusal: the extractor returns nothing, or leaves the unread word
in the remainder, rather than guessing.  Each pin turns into a failing test the
day someone adds the vocabulary, which is exactly when the behaviour should be
revisited.
"""
import pytest

from chronologia.extract.numfold_welsh import CARDINALS

from ._corpus import nomatch, parse, remainder


@pytest.mark.parametrize("text", ["trennydd", "drennydd", "tradwy"])
def test_no_day_after_tomorrow(text):
    """"trennydd" appears on a dictionary entry only as the cross-referenced
    antonym of "echdoe", with no running-text occurrence found at all and a
    second spelling in circulation, so the day two ahead is not named."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["eleni", "llynedd"])
def test_no_single_word_year_deixis(text):
    """Welsh has dedicated adverbs for "this year" and "last year", but no
    construction here reads a bare year-deictic adverb, so they are left
    unread rather than wired to an approximation."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ers dydd Llun", "ers blynyddoedd", "er 1990",
])
def test_no_since_marker(text):
    """"ers"/"er" are attested as "since"/"for", but their governed forms and
    the register split between them were never pinned down, so no open-range
    vocabulary ships."""
    r = parse(text)
    assert r is None or "ers" in r[1] or "er" in r[1]


@pytest.mark.parametrize("text", [
    "am dair blynedd", "am ddwy wythnos", "am bum munud",
])
def test_no_duration_for(text):
    """"am" is shipped only as the clock preposition ("am dri o'r gloch");
    its durational sense ("am awr" -- for an hour) has no separate marker, so
    a duration phrase must not read as one."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "o Fehefin i Awst", "o Ionawr i Fawrth", "rhwng Mehefin a Medi",
])
def test_no_from_to_or_between_range(text):
    """No worked example fixed the governed forms of a two-ended range, so no
    range vocabulary ships and the phrase cannot close a span."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "cyn ddydd Llun", "ar ôl dydd Llun", "tan ddydd Llun",
])
def test_no_before_after_or_until_marker(text):
    """"cyn" (before) is attested as a soft-mutation trigger with a worked
    example, but "ar ôl" and "tan" are not, and shipping one edge of the
    family alone would read a bounded phrase as an unbounded one."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["mileniwm", "dau fileniwm", "ymhen mileniwm"])
def test_no_millennium_unit(text):
    """The dictionary has no Welsh entry for a millennium noun at all, so the
    unit is absent rather than transliterated."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "y gwanwyn", "yr haf", "y gaeaf", "haf 2020",
])
def test_no_season_vocabulary(text):
    """The Welsh word for autumn is spelled exactly like the month October
    ("Hydref"), so a season table would make every October a season and every
    autumn a month; the whole family is left out until the collision is
    resolved deliberately."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["y penwythnos", "penwythnos"])
def test_no_weekend_reference(text):
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "44 CC", "1990 OC", "cyn Crist",
])
def test_no_era_vocabulary(text):
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["dechrau Mehefin", "diwedd Mehefin"])
def test_period_part_is_left_in_the_remainder(text):
    """No early/mid/late vocabulary ships, so the unread part word must stay
    visible in the remainder."""
    assert remainder(text) != ""


@pytest.mark.parametrize("text", ["3ydd chwarter", "chwarter cyntaf"])
def test_no_calendar_quarter(text):
    """"chwarter" is shipped as the clock fraction only; the calendar quarter
    sense would need its own attested construction."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["wythnos 3", "3ydd wythnos"])
def test_no_iso_week_reference(text):
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("surface", [
    "deugain ac un", "hanner cant ac dau", "trigain ac tri",
    "pedwar ugain ac un",
])
def test_the_ac_joined_vigesimal_compounds_are_not_read(surface):
    """The numeral appendix joins 41..99 with "ac" before a consonant, which
    the coordinator's own attested alternation contradicts; rather than pick a
    side those compounds are omitted, and the decimal spelling covers the
    range."""
    assert surface not in CARDINALS


@pytest.mark.parametrize("text", ["mil naw chwe pump", "mil naw wyth deg"])
def test_no_digit_group_year_reading(text):
    """Welsh reads a year by digit groups ("mil naw chwe pump" for 1965), a
    reading no construction here implements; the phrase must not resolve to a
    year by some other route."""
    r = parse(text)
    assert r is None or r[0].start.year != 1965


@pytest.mark.parametrize("text", ["ym mis Mawrth", "ym mis Ionawr"])
def test_the_locative_month_word_is_left_unread(text):
    """"ym mis Mawrth" (in March) is attested, but "mis" as a month-word
    introducer has no slot here, so it stays in the remainder rather than
    being silently swallowed."""
    assert remainder(text) != ""


@pytest.mark.parametrize("text", ["dydd Llun nesaf yn y bore"])
def test_the_articled_daypart_phrase_is_partly_unread(text):
    """"yn y bore" (in the morning) needs a locative construction this locale
    does not ship."""
    assert remainder(text) != ""


@pytest.mark.parametrize("text", ["3 diwrnod", "dwy flynedd", "pum mlynedd"])
def test_a_spelled_quantity_needs_a_marker(text):
    nomatch(text)
