"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Irish surfaces could not be
attested, or whose sources contradict one another, so no vocabulary ships for
it.  The contract is refusal: the extractor returns nothing, or leaves the
unread word in the remainder, rather than guessing.  Each pin turns into a
failing test the day someone adds the vocabulary, which is exactly when the
behaviour should be revisited.
"""
import pytest

from ._corpus import nomatch, parse, remainder


@pytest.mark.parametrize("text", [
    "mílaois", "an tríú mílaois", "dhá mhílaois ó shin",
])
def test_no_millennium(text):
    """"mílaois" is an attested noun but no source gives its genitive, its
    plural or any counted form, so no millennium unit ships."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "deich mbliana", "trí deich mbliana ó shin", "na seachtóidí",
])
def test_no_decade(text):
    """Irish has no single-word "decade" attested; the compositional "deich
    mbliana" is ten years, not a named decade, and reading it as one would
    turn a duration into a calendar period."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "an fichiú haois", "an chéad haois", "trí chéad ó shin",
])
def test_no_century(text):
    """"céad" is at once "hundred", "century" and "first", and the sources
    contradict each other on whether it mutates what follows it.  No century
    unit ships rather than one that conflates a hundred years with the first
    of something."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["an chéad lá", "an chéad uair", "chéad"])
def test_lenited_cead_is_not_a_number(text):
    """The lenited "chéad" is the ordinal "first" after the article, never
    the numeral hundred; folding it to 100 would invent a quantity."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ceithre bliana déag ó shin", "aon bhliain déag ó shin",
])
def test_no_split_teen_around_a_counted_noun(text):
    """A counted teen puts the noun INSIDE the numeral ("ceithre bliana
    déag"); no source gives that shape for more than one noun, so the fold
    refuses it rather than reading the leading element alone."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "an t-aonú lá is tríocha", "aonú is tríocha", "tríochadú lá is aon",
])
def test_no_thirty_first_ordinal(text):
    """The numerals table runs to the thirtieth; the thirty-first is only
    described as a pattern, never spelled, so it is not read."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["ceathrú Meitheamh", "an ceathrú lá"])
def test_fourth_is_not_a_spelled_ordinal(text):
    """"ceathrú" is at once "fourth" and the quarter of an hour the clock
    speaks, so the fold refuses to claim every occurrence of it as the digit
    4; reading it as an ordinal would erase the quarter from every clock
    phrase."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "maidin", "ar maidin", "tráthnóna", "san oíche", "nóin",
])
def test_no_dayparts(text):
    """Unicode CLDR has no day-period rule set for Irish at all -- its
    authority stops at the bare am/pm markers -- so no time-of-day band
    ships and a daypart word is left unread."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "samhradh", "an geimhreadh", "earrach 2020", "fómhar",
])
def test_no_seasons(text):
    """No season vocabulary was attested for this locale, so a season word
    never resolves to a quarter of the year."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "44 RC", "an bhliain 1990 AD", "roimh Chríost",
])
def test_no_era_vocabulary(text):
    """No era marker ships, so an era-qualified year is either refused or
    leaves the marker visible."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["i gceann trí lá", "faoi cheann seachtaine"])
def test_no_forward_offset_marker(text):
    """No "in <N> <units>" forward marker was attested, so a forward offset
    is refused rather than read with the backward marker's sign."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "ar feadh trí lá", "ar feadh bliana", "ar feadh dhá uair",
])
def test_duration_alone_is_not_a_span(text):
    """"ar feadh" states how long something lasts, not when it happens; on
    its own it anchors nothing and must not become an offset."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "gach Luan", "gach uile bhliain", "gach huair",
])
def test_every_is_left_unread(text):
    """"gach" imposes h-prothesis on some nouns, lenition on others and
    nothing on the rest, with no rule any source states, so only the bare
    marker ships and the mutated collocations are not read."""
    r = parse(text)
    assert r is None or "gach" in r[1]


@pytest.mark.parametrize("text", ["ó mhaidin", "ó Shamhain"])
def test_lenition_after_o_is_not_read(text):
    """The same preposition "ó" lenites in one of its own cited examples and
    leaves the radical in another; the contradiction is not resolved by
    picking a side, so only the unmutated reading ships."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["idir fhir agus mhná", "idir Luan agus Mháirt"])
def test_lenited_between_is_not_a_date_range(text):
    """"idir ... agus ..." lenites both conjuncts only in its "both ... and
    ..." sense, which is not a date range; the plain unmutated reading is
    the one that ships."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["3ú seachtain", "seachtain 3"])
def test_no_iso_week_reference(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["ag tús Meitheamh", "i ndeireadh Meitheamh"])
def test_period_part_is_left_in_the_remainder(text):
    """No early/mid/late vocabulary ships, so the unread part word must stay
    visible in the remainder."""
    assert remainder(text) != ""
