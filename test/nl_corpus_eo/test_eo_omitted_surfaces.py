"""Documented refusals -- vocabulary this locale deliberately does not ship,
because the source citations for it are missing or contradictory, rather
than silently guessing a wrong surface.

Dayparts: CLDR 47 ships Esperanto only the coarse am/pm dayPeriod pair, with
no morning/afternoon/evening/night band boundaries in the supplemental
dayPeriodRuleSet (eo falls back to the root am/pm-only default).  The four
colloquial daypart words (matene/posttagmeze/vespere/nokte) exist in the
lexicon, but inventing band boundaries for them has no CLDR authority, so
neither the daypart words nor a meridiem am/pm marker are shipped.

Year-inclusive absolute dates: the exact construction for "the first of
January 2024" (does the year take its own connector, "en"/"de la jaro", or
sit bare after the month?) was not found in an independently fetched
source, so only the day+month form is wired; a trailing year is left
unconsumed rather than guessed at.

Relative weekday shift ("last/next Monday"): the only attested surfaces are
FUSED compounds ("pasintlunde", "sekvalunde"), themselves adverbial -e
forms whose semantics (single occurrence vs recurring) are not resolved by
the citation that lists them (see test_eo_weekday_case.py) -- a two-word
"pasinta lundon" is not attested, so it is not wired either.
"""
import pytest

from ._corpus import nomatch, remainder


@pytest.mark.parametrize("text", ["matene", "posttagmeze", "vespere", "nokte"])
def test_daypart_words_are_not_wired(text):
    nomatch(text)


def test_daypart_after_a_clock_reading_is_left_unconsumed():
    """"je la sesa vespere" ("at six in the evening") parses only the clock
    part; "vespere" is left stranded in the remainder rather than being
    silently dropped or misread as a fine-grained band."""
    r = remainder("je la sesa vespere")
    assert "vespere" in r


def test_year_inclusive_date_leaves_the_year_unconsumed():
    r = remainder("la unua de januaro 2024")
    assert r.strip() == "2024"


@pytest.mark.parametrize("word,text", [
    ("pasinta", "pasinta lundon"), ("sekva", "sekva lundon"),
    ("venonta", "venonta lundon"),
])
def test_relative_weekday_shift_is_not_wired(word, text):
    """No REL_MARKER vocabulary is shipped for these words, so the
    (unattested) two-word shift never fires: only the bare accusative
    weekday resolves, and the leading word is left stranded in the
    remainder rather than silently folded into a wrong shifted date."""
    r = remainder(text)
    assert word in r
