"""What this locale declines to answer, and why each refusal is the answer.

Every case here is an omission with a reason.  A locale that guessed at any of
them would return a confident wrong span for text a Maltese speaker writes,
which is worse than returning nothing, so each refusal is pinned as hard as
the readings that do ship.
"""
import pytest

from ._corpus import nomatch, parse, span


# -- no dayparts ------------------------------------------------------------
# CLDR ships no dayPeriodRuleSet for Maltese at all -- only the borrowed AM
# and PM labels -- so there are no band boundaries to transcribe and none are
# invented from a dictionary gloss.  filgħodu and filgħaxija ship as clock
# markers, which fix a spoken hour in the AM or PM half; they do not name a
# span of their own.

@pytest.mark.parametrize("text", [
    "filgħodu", "filgħaxija", "bil-lejl", "wara nofsinhar",
])
def test_no_daypart_band_is_asserted(text):
    r = parse(text)
    assert r is None or r[1] != ""


def test_the_morning_word_still_works_as_a_clock_marker():
    assert span("fis-sebgħa filgħodu").start.hour == 7


# -- no day before yesterday ------------------------------------------------
# CLDR carries no relative-type--2 field for mt and no other source names the
# word, so no surface is shipped.  The day AFTER tomorrow is sourced and does
# ship, which is what makes the asymmetry deliberate rather than an oversight.

@pytest.mark.parametrize("text", [
    "qabel ilbieraħ", "qabel lbieraħ", "ilbieraħ l-ieħor",
])
def test_the_day_before_yesterday_is_not_guessed(text):
    r = parse(text)
    assert r is None or r[0].start.date().isoformat() != "2027-05-10"


def test_the_day_after_tomorrow_does_ship():
    assert span("pitgħada").start.date().isoformat() == "2027-05-14"


# -- no decade, no millennium ----------------------------------------------
# Neither deċennju nor millennju has a dictionary entry to cite, so neither
# unit ships; the century, which does, is the largest unit this locale counts.

@pytest.mark.parametrize("text", [
    "deċennju ilu", "millennju ilu", "żewġ deċennji ilu",
])
def test_decade_and_millennium_are_not_shipped(text):
    nomatch(text)


def test_the_century_does_ship():
    assert span("seklu ilu").start.year == 1927


# -- the future frame needs its trailing "another" -------------------------
# Both directions of an offset are marked at the TAIL: ilu for the past, oħra
# for the future.  A frame word alone ("fi żmien sena") carries no tail
# marker, and the only way to sign it would be to accept a preposed direction
# marker -- which would also accept the preposed durative ilu this locale must
# never read as "ago".  The count-one and count-two CLDR patterns that omit
# oħra are refused on that trade.

@pytest.mark.parametrize("text", [
    "fi żmien sena", "fi żmien sagħtejn", "fi żmien ġurnata",
])
def test_a_future_frame_without_the_trailing_marker_is_refused(text):
    nomatch(text)


def test_the_same_offset_with_the_trailing_marker_reads():
    assert span("fi żmien sena oħra").start.year == 2028


# -- foreign phrasings must not read as Maltese -----------------------------

@pytest.mark.parametrize("text", [
    "منذ يومين", "לפני יומיים", "due giorni fa", "fa due giorni",
    "hace dos días", "il y a deux jours",
])
def test_a_sibling_or_source_language_phrasing_is_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date().isoformat() == "2027-05-12"


# -- junk -------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "", "   ", "bonġu kif int", "qwerty zxcvb", "m'hawn ebda data hawn",
])
def test_junk_is_none(text):
    nomatch(text)


def test_a_month_name_inside_a_word_is_not_a_month():
    nomatch("marzupan")
