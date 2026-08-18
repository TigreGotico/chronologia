"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Hindi surfaces could not be
attested to a dictionary source, or whose word order the engine has no grammar
for.  The contract is refusal: the extractor returns nothing, or leaves the
unread word visible in the remainder, rather than guessing.  Each pin turns
into a failing test the day someone adds the vocabulary or the grammar, which
is exactly when the behaviour should be revisited.
"""
import pytest

from ._corpus import nomatch, parse, remainder


@pytest.mark.parametrize("text", ["प्रथम", "द्वितीय", "तृतीय", "दशम",
                                  "द्वितीय दिन", "प्रथम सदी"])
def test_the_sanskritic_ordinals_are_not_shipped(text):
    """प्रथम / द्वितीय / तृतीय / दशम are a separate learned register from the
    vernacular पहला / दूसरा / तीसरा / दसवाँ series that ships.  Mixing the two
    would need the register's own paradigm, so it is left out."""
    nomatch(text)


@pytest.mark.parametrize("text", ["बृहस्पतिवार", "बृहस्पतिवार को"])
def test_the_formal_thursday_is_not_shipped(text):
    """en.wiktionary carries बृहस्पतिवार only as a SANSKRIT entry; the Hindi
    गुरुवार entry names it a synonym but the word has no Hindi entry of its
    own, so it is not attested for this locale."""
    nomatch(text)


@pytest.mark.parametrize("text", ["चैत्र", "वैशाख", "फाल्गुन"])
def test_the_vikram_samvat_months_are_not_implemented(text):
    """The Hindu lunisolar calendar's month names, its leap month and its
    per-month year offset are a calendar implementation, not vocabulary."""
    nomatch(text)


def test_a_vikram_samvat_year_is_not_converted():
    """The numeral still reads as the Gregorian year it spells, and the era
    name stays unread -- the +57 conversion is never silently applied."""
    r = parse("2081 विक्रम संवत")
    assert r is not None
    assert r[0].start.year == 2081
    assert "विक्रम" in r[1]


@pytest.mark.parametrize("text", [
    "छह बजे से दस बजे तक",
    "सोमवार से शुक्रवार तक",
    "मार्च से जून तक",
])
def test_a_closed_range_leaves_its_far_bound_unread(text):
    """Hindi frames a closed range with BOTH markers postposed -- "A से B तक",
    the start closed by से and the end by तक.  The range grammar reads a
    LEADING frame ("from A to B"), so only the open reading fires and the far
    bound stays visible in the remainder rather than being silently dropped.
    The open ranges themselves ("शुक्रवार तक", "सोमवार से") do resolve."""
    r = parse(text)
    assert r is not None
    assert r[1] != ""
    assert "से" in r[1] or "तक" in r[1]


@pytest.mark.parametrize("text", [
    "2010 और 2020 के बीच", "सोमवार और शुक्रवार के बीच",
])
def test_a_between_range_leaves_its_far_bound_unread(text):
    """के बीच is attested as "between" (en.wiktionary, entry "के बीच") but it
    TRAILS both bounds, and the between-grammar reads a leading frame."""
    r = parse(text)
    assert r is not None
    assert "के बीच" in r[1]


@pytest.mark.parametrize("text", ["दस बजने को सात मिनट", "बजने को"])
def test_the_minutes_to_frame_is_not_read(text):
    """"N बजने को M मिनट" counts M minutes short of the Nth hour.  Wiring it
    would need a subtractive clock direction spelled as a two-word verbal
    frame, which no existing order shape expresses, so it is refused."""
    nomatch(text)


@pytest.mark.parametrize("text", ["जून की शुरुआत", "जून के अंत", "जून के मध्य"])
def test_period_parts_are_left_in_the_remainder(text):
    """No early/mid/late vocabulary could be attested as a fixed temporal
    qualifier, so the whole month is returned and the unread words stay
    visible."""
    assert remainder(text) != ""


@pytest.mark.parametrize("text", ["पहली तिमाही", "तिमाही", "दूसरी तिमाही"])
def test_no_calendar_quarter(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["सप्ताह 3", "3 सप्ताह", "तीसरा सप्ताह"])
def test_no_iso_week_reference(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["44 ईसा पूर्व", "ईसा पूर्व", "ईसवी सन 1947"])
def test_no_era_vocabulary(text):
    """The era abbreviations could not be attested, so an era-qualified year
    is either refused or leaves the era word unread."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["एक लाख साल पहले", "दो करोड़ साल पहले"])
def test_the_large_indian_scale_words_are_not_shipped(text):
    """लाख (10^5) and करोड़ (10^7) are everyday Hindi but never name a date;
    they belong to a deep-time scale vocabulary this locale does not ship."""
    nomatch(text)


def test_the_midnight_compound_is_not_read():
    """आधी रात is the everyday phrase for midnight, but आधी is the half-word
    the fractional constructions read and रात the night BAND.  No compound
    landmark ships, so the band is returned and आधी stays in the remainder --
    mid-band rather than silently wrong, and honest about it."""
    r = parse("आधी रात")
    assert r is not None
    assert "आधी" in r[1]
    assert r[0].start.hour == 20
