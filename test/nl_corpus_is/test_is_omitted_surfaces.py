"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Icelandic surfaces could not be
attested to a dictionary source, so no vocabulary ships for it.  The contract
is refusal: the extractor returns nothing, or leaves the unread word in the
remainder, rather than guessing.  Each pin turns into a failing test the day
someone adds the vocabulary, which is exactly when the behaviour should be
revisited.
"""
import pytest

from ._corpus import nomatch, parse, remainder


@pytest.mark.parametrize("text", [
    "hinn daginn", "eftir tvo daga daginn", "yfirmorgun",
])
def test_no_day_after_tomorrow(text):
    """The one candidate a search turned up for "the day after tomorrow"
    ("hinn daginn") ordinarily means "the other day", and no compositional
    form was attested either.  The token is left unread rather than guessed,
    so the phrase never names a day two ahead."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "frá og með mánudegi", "síðan á mánudag", "síðan í gær",
])
def test_no_since_marker(text):
    """"frá og með" was never confirmed by a fetched source, so no "since"
    vocabulary ships and an anchored open range is refused."""
    r = parse(text)
    assert r is None or "síðan" in r[1] or "frá" in r[1]


@pytest.mark.parametrize("text", [
    "í þrjá daga", "í tvær vikur", "í fimm mínútur",
])
def test_no_duration_for(text):
    """The "for <duration>" marker has no citation, so a duration phrase must
    not be read as one."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "á hverjum degi", "hvern dag", "á hverjum mánudegi",
])
def test_no_every_quantifier(text):
    """No "every" quantifier was independently fetched, so a recurrence
    phrase does not resolve to one."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "frá júní til ágúst", "frá janúar til mars",
])
def test_no_from_to_range(text):
    """The governed cases of "frá"/"til" were never verified with a worked
    example, so no range vocabulary ships and the phrase cannot close a
    two-ended span."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "milli júní og september", "milli mánudags og föstudags",
])
def test_no_between_and_range(text):
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "áður en við hittumst", "eftir að hann hætti",
])
def test_clause_conjunctions_are_not_offset_markers(text):
    """"áður en" and "eftir að" introduce a CLAUSE, not a quantity; reading
    either as the prepositional "fyrir"/"eftir" would invent an offset."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["annar júní", "annar desember"])
def test_second_is_not_a_spelled_day(text):
    """"annar" is the ordinary Icelandic word for "another"/"the other", so
    the ordinal fold refuses to claim every occurrence of it as the digit 2;
    the dotted form "2. júní" is how the second is read."""
    r = parse(text)
    assert r is None or "annar" in r[1] or r[0].start.day != 2


@pytest.mark.parametrize("text", [
    "fyrsti ársfjórðungur", "annar ársfjórðungur", "ársfjórðungur",
])
def test_no_calendar_quarter(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["3. vika", "vika 3", "þriðja vika"])
def test_no_iso_week_reference(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "44 f.Kr.", "árið 1990 e.Kr.", "fyrir Krist",
])
def test_no_era_vocabulary(text):
    """No era marker ships, so an era-qualified year is either refused or
    leaves the marker visible."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["í byrjun júní", "í lok júní"])
def test_period_part_is_left_in_the_remainder(text):
    """No early/mid/late vocabulary ships, so the unread part word must stay
    visible in the remainder."""
    assert remainder(text) != ""


@pytest.mark.parametrize("text", ["þrjú hundruð og fimmtíu dagar"])
def test_spelled_quantity_needs_a_marker(text):
    """A spelled quantity is still only a quantity without a direction
    marker."""
    nomatch(text)
