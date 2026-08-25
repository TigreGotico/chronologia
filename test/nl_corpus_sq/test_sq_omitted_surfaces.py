"""What the Albanian locale deliberately does NOT claim.

Each case below is a construction whose Albanian form no reachable source
settled: the surface candidates exist in word lists, but none came with a
worked example or a statement of the case it governs.  Shipping a guess would
produce a confident wrong span, so the locale ships nothing and these tests
pin the silence -- they fail the day a surface is added without the evidence
to justify it, and they are the checklist for the pass that adds it.
"""
import pytest

from ._corpus import ANCHOR, nomatch, parse


@pytest.mark.parametrize("text", [
    "që nga e hëna", "që nga dje", "që prej një jave",
])
def test_since_is_not_implemented(text):
    """``që nga`` / ``që prej`` are both listed as "since" in word lists, with
    no example fixing which one a temporal phrase takes or what case it
    governs."""
    r = parse(text)
    assert r is None or "që" in r[1]


@pytest.mark.parametrize("text", [
    "midis e hënë dhe e premte", "ndërmjet dy javësh", "në mes të javës",
])
def test_between_and_is_not_implemented(text):
    """``midis``/``ndërmjet``/``në mes`` all surfaced as "between", none with
    a two-endpoint example, so no range marker is claimed."""
    r = parse(text)
    assert r is None or any(w in r[1] for w in ("midis", "ndërmjet", "mes"))


@pytest.mark.parametrize("text", ["për tre ditë", "për një javë"])
def test_for_duration_is_not_implemented(text):
    """``për`` is "for" in every preposition list, but with no temporal
    worked example it is not shipped as a duration marker."""
    r = parse(text)
    assert r is None or "për" in r[1]


@pytest.mark.parametrize("text", [
    "dekadë", "dhjetëvjeçar", "mijëvjeçar", "tre dekada më parë",
    "një mijëvjeçar më parë",
])
def test_decade_and_millennium_have_no_vocabulary(text):
    """Neither a decade word nor a millennium word has a dictionary entry that
    could be read, so those units are absent rather than transliterated."""
    r = parse(text)
    assert r is None or r[1]


@pytest.mark.parametrize("text", [
    "shekulli XXI", "shekulli 21", "shekulli i njëzetenjëtë",
])
def test_the_postposed_century_ordinal_refuses(text):
    """Albanian writes the century with the ordinal AFTER the noun.  Reading
    that order would also swallow "viti 2027" (a year word plus a year), so
    the postposed form waits for an ordinal-position mechanism instead of
    being bought at that price -- and until then the phrase returns NOTHING.
    Falling through to a bare-hour clock, which answered "shekulli XXI" with
    21:00, is the failure this pins: the century is unreadable, so the only
    honest answer is none, exactly as English gives for "century XXI"."""
    nomatch(text)


def test_the_year_word_still_names_its_year():
    """The regression the refusal above buys its safety from: a year word plus
    a year is not a postposed ordinal and must keep resolving."""
    r = parse("viti 2027")
    assert r is not None and r[1] == ""
    assert (r[0].start.year, r[0].start.month, r[0].start.day) == (2027, 1, 1)


def test_the_hour_word_licenses_a_bare_hour():
    """A bare number reads as a clock only when the hour word introduces it,
    which is what keeps a stray numeral after any noun from becoming a time."""
    r = parse("ora tetë")
    assert r is not None and (r[0].start.hour, r[0].start.minute) == (8, 0)
    nomatch("tetë")


def test_the_feminine_first_is_not_folded():
    """The feminine ordinal "e para" is homographic with the preposition
    ``para`` ("before/ago"); no reading of the bare word tells them apart, so
    only the masculine ``parë`` is in the fold."""
    r = parse("e para e qershorit")
    assert r is None or "para" in r[1]


def test_para_stays_a_preposition():
    """The corollary: the ago-marker reading of ``para`` is untouched."""
    s = parse("para dy ditësh")
    assert s is not None and s[1] == ""
    assert s[0].start.day == ANCHOR.day - 2


@pytest.mark.parametrize("text,month", [("mar 2020", 3), ("sht 2020", 9)])
def test_the_colliding_abbreviations_are_months_not_weekdays(text, month):
    """CLDR's abbreviated Tuesday and Saturday ("mar", "sht") are spelled
    exactly like abbreviated March and September.  The month reading is the
    one that carries a year, so the weekday abbreviations for those two days
    are not shipped and the abbreviation stays unambiguous."""
    r = parse(text)
    assert r is not None and r[0].start.month == month


@pytest.mark.parametrize("text", ["e diela", "e hëna", "e marta"])
def test_the_definite_weekday_forms_are_not_shipped(text):
    """CLDR gives the citation form ("e diel") and the two forms the relative
    frames use ("të diel", "të dielën").  The definite nominative is attested
    for only two of the seven days, so none of the seven ships it."""
    nomatch(text)


def test_the_ordinal_day_of_month_is_not_read():
    """Whether an Albanian date names its day with a cardinal or an ordinal,
    and where the connective goes, was never attested; the locale reads only
    the CLDR pattern ("d MMMM y", a bare cardinal day)."""
    r = parse("e pesta ditë e qershorit")
    assert r is None or r[1]


def test_the_cldr_date_order_is_what_ships():
    r = parse("5 qershor 2027")
    assert r is not None and r[1] == ""
    assert (r[0].start.year, r[0].start.month, r[0].start.day) == (2027, 6, 5)
