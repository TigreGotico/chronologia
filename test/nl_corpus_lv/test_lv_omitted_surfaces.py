"""What this locale deliberately does not read, pinned so it stays honest.

Every phrase below names a construction whose Latvian surfaces could not be
attested to a source, so no vocabulary ships for it.  The contract is
refusal: the extractor returns nothing, or leaves the unread word in the
remainder, rather than guessing.  Each pin turns into a failing test the day
someone adds the vocabulary, which is exactly when the behaviour should be
revisited.
"""
import pytest

from ._corpus import nomatch, parse


@pytest.mark.parametrize("text", [
    "otrdien", "trešdien", "ceturtdien", "piektdien", "sestdien", "svētdien",
])
def test_short_adverbial_weekdays_beyond_monday(text):
    """"pirmdien" is attested in running text and ships; the same shape for
    the other six days is a regular pattern that no dictionary or corpus
    consulted confirms, so those six are refused rather than derived."""
    nomatch(text)


def test_the_attested_short_adverbial_does_ship():
    """The control for the pin above: Monday's form is not refused."""
    assert parse("pirmdien") is not None


@pytest.mark.parametrize("text", ["pusviens", "pusviena"])
def test_the_half_hour_toward_one(text):
    """12:30 would be "pus" + the cardinal one, but one is the single Latvian
    cardinal in the naming range that declines for gender and number, and no
    source gives the compound.  Guessing between the two candidates is the
    thing this pin prevents."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "bez piecām minūtēm trīs", "bez ceturkšņa trīs", "ceturksnis pāri trim",
])
def test_no_minutes_to_or_past_the_hour(text):
    """Only the half hour is sourced; the counting-down and quarter-hour
    clock phrasings are not, so they do not ship."""
    nomatch(text)


@pytest.mark.parametrize("text", ["maija 5", "5 maija", "2017. gada maija"])
def test_no_genitive_date(text):
    """A Latvian date names its month in the nominative (dateline) or the
    locative (adverbial).  A genitive month is an attributive phrase, not a
    date, and reading it as one was the error this locale was built to
    avoid."""
    r = parse(text)
    assert r is None or "maija" in r[1]


@pytest.mark.parametrize("text", [
    "no jūnija līdz augustam", "starp jūniju un septembri",
])
def test_no_month_range(text):
    """A Latvian range puts its endpoint months in the genitive and the
    dative, the very cases the date constructions exclude; rather than admit
    them into the month vocabulary and resurrect the genitive date, the range
    is left unread."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", [
    "pēc 45 sekundēm", "pirms 30 sekundēm",
])
def test_no_second_unit(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "pirmais ceturksnis", "ceturksnis", "otrais ceturksnis",
])
def test_no_calendar_quarter(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["3. nedēļa", "nedēļa 3", "trešā nedēļa"])
def test_no_iso_week_reference(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "44. gads pirms mūsu ēras", "pirms mūsu ēras",
])
def test_no_era_vocabulary(text):
    r = parse(text)
    assert r is None or "ēras" in r[1] or "mūsu" in r[1]


@pytest.mark.parametrize("text", ["nedēļas nogale", "brīvdienas"])
def test_no_weekend_reference(text):
    """"nedēļas nogale" is two words whose first is already the unit noun
    "week", and "brīvdiena" is a day off rather than the weekend; neither is
    a surface this locale can bind without inventing one."""
    r = parse(text)
    assert r is None or r[1] != ""


@pytest.mark.parametrize("text", ["jūnija sākumā", "jūnija beigās"])
def test_no_period_part(text):
    """No early/mid/late vocabulary ships."""
    r = parse(text)
    assert r is None or r[1] != ""


def test_the_last_determiner_ships_only_in_the_locative():
    """CLDR gives "pagājušajā <unit>" and nothing else declines the
    participle in a dictionary consulted, so the nominative determiner is not
    a marker here and must not be silently swallowed."""
    r = parse("pagājušais gads")
    assert r is None or "pagājušais" in r[1]


def test_the_year_word_alone_does_not_make_a_year():
    """"2019. gadā" needs the year word to bind the bare year, and the shape
    it would have to take collides with the scoped-ordinal reading of the
    same two tokens; rather than force it, the bare year is what ships."""
    assert parse("2019. gadā") is None
    assert parse("2019") is not None


@pytest.mark.parametrize("text", ["katru nedēļu", "katru pirmdienu"])
def test_recurrence_marker_is_left_in_the_remainder(text):
    """"katrs" is a sourced distributive, but no recurrence construction
    binds it here, so it stays visible instead of being consumed."""
    r = parse(text)
    assert r is None or "katru" in r[1]
