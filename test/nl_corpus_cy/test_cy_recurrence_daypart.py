"""Welsh recurrence under "bob", and the three day-part bands CLDR draws.

"bob" is the every-marker: it is itself the lexicalised soft mutation of
"pob", and it is the form the distributive construction uses ("bob dydd Llun"
-- every Monday).  A count between the marker and the noun sets the interval,
and the year's count form carries its mutation there too ("bob dwy flynedd",
"bob pum mlynedd").

Welsh CLDR draws only THREE day-part bands -- a morning that opens at midnight
and runs to noon, an afternoon to 18:00 and an evening to midnight -- and no
night rule at all, so this locale ships no night surface and none is invented.
"""
import pytest

from ._corpus import ANCHOR, ad, nomatch, recur, span

#: midnight of the anchor day -- the civil day a bare day-part names.
_TODAY = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)

#: weekday index of each Welsh day name; 0 is Monday.
WEEKDAYS = [("Llun", 0), ("Mawrth", 1), ("Mercher", 2), ("Iau", 3),
            ("Gwener", 4), ("Sadwrn", 5), ("Sul", 6)]


@pytest.mark.parametrize("text,freq", [
    ("bob dydd", "DAILY"), ("bob wythnos", "WEEKLY"),
    ("bob mis", "MONTHLY"), ("bob blwyddyn", "YEARLY"),
])
def test_bob_plus_unit_names_the_frequency(text, freq):
    got = recur(text)
    assert got is not None
    assert got.recurrence.freq == freq
    assert got.recurrence.interval == 1
    assert got.remainder == ""


@pytest.mark.parametrize("text,freq", [
    ("pob dydd", "DAILY"), ("pob wythnos", "WEEKLY"),
])
def test_the_radical_pob_is_read_as_well(text, freq):
    """The unmutated citation form is rarer in this construction but real
    ("Mae pob dydd yn wahanol"), so it is read too."""
    got = recur(text)
    assert got is not None and got.recurrence.freq == freq


@pytest.mark.parametrize("name,index", WEEKDAYS)
def test_bob_plus_weekday_recurs_weekly_on_that_day(name, index):
    got = recur(f"bob dydd {name}")
    assert got is not None
    assert got.recurrence.freq == "WEEKLY"
    assert got.recurrence.byday == ((None, index),)


@pytest.mark.parametrize("text,freq,interval", [
    ("bob dwy flynedd", "YEARLY", 2),
    ("bob tair blynedd", "YEARLY", 3),
    ("bob pum mlynedd", "YEARLY", 5),
    ("bob dau fis", "MONTHLY", 2),
    ("bob tair wythnos", "WEEKLY", 3),
    ("bob tri diwrnod", "DAILY", 3),
])
def test_a_count_between_bob_and_the_noun_sets_the_interval(text, freq,
                                                            interval):
    got = recur(text)
    assert got is not None
    assert (got.recurrence.freq, got.recurrence.interval) == (freq, interval)


@pytest.mark.parametrize("text", ["bob", "pob", "dydd Llun"])
def test_no_recurrence_without_the_marker_and_a_unit(text):
    got = recur(text)
    assert got is None or got.recurrence.freq is None


@pytest.mark.parametrize("text,h0,h1", [
    ("bore", 0, 12), ("prynhawn", 12, 18), ("hwyr", 18, 0),
])
def test_the_three_cldr_bands(text, h0, h1):
    s = span(text)
    assert s.start.hour == h0
    assert s.end.hour == h1


def test_the_mutated_morning_matches_the_radical():
    # A bare day-part is not future-shifted, so it names the anchor day's band.
    assert (span("bore").start, span("bore").end) == (
        ad(_TODAY), ad(_TODAY.replace(hour=12)))
    assert span("fore") == span("bore")


def test_the_mutated_afternoon_matches_the_radical():
    assert (span("prynhawn").start, span("prynhawn").end) == (
        ad(_TODAY.replace(hour=12)), ad(_TODAY.replace(hour=18)))
    assert span("brynhawn") == span("prynhawn")


@pytest.mark.parametrize("text", ["nos", "noson", "noswaith"])
def test_no_night_band_ships(text):
    """Welsh CLDR states no night rule, so no night vocabulary ships and a
    night word does not resolve to a band."""
    nomatch(text)
