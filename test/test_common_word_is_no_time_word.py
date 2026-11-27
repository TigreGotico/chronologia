"""A common word is no time word when its other sense is the one meant.

en "fall" after "will" is a verb; en modal "may" before a verb is no month; da
"går" is the verb "to go" and "i går" is yesterday; da "her til morgen" is this
morning, not tomorrow; oc "per ora" is "per hour"; pl "lata" after
"przyszłego" is the genitive of "lato" (summer); nb and nn "går" is a verb
unless "i" stands before it.  The expected values are the ones the issue
states.  Anchors: Tuesday 2017-06-27 13:04 Europe/Lisbon, and for the two
marked rows 2026-11-22 09:00 and 2026-10-17 12:00 Europe/Lisbon.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from chronologia import extract_timespan

ISSUE = "https://github.com/TigreGotico/chronologia/issues/990"
LISBON = ZoneInfo("Europe/Lisbon")
ANCHOR = datetime(2017, 6, 27, 13, 4, tzinfo=LISBON)
MAY_ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=LISBON)

NO_DATE = [
    ("oc", "Quants quilomètres per ora fa lo vent?", ANCHOR),
    ("en", "the last third may be the hardest", datetime(2026, 11, 22, 9, 0)),
    ("en", "it may be late", MAY_ANCHOR),
    ("en-US", "it may second guess", MAY_ANCHOR),
    ("en-US", "i may third that", MAY_ANCHOR),
    ("nb", "hei hvordan går det", ANCHOR),
    ("nn", "hei korleis går det", ANCHOR),
]


def test_da_gaar_without_i_is_the_verb():
    assert extract_timespan("Hvornår går det løs med at regne?", "da", ANCHOR) is None


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
@pytest.mark.parametrize("lang,text,anchor", NO_DATE)
def test_the_common_sense_names_no_date(lang, text, anchor):
    assert extract_timespan(text, lang, anchor) is None


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_en_fall_before_friday_night_leaves_friday_night_the_date():
    found = extract_timespan(
        "how far will the temperature fall on Friday night", "en", ANCHOR)
    assert found.span.start.datetime().date() == datetime(2017, 6, 30).date()


def test_da_her_til_morgen_is_this_morning():
    found = extract_timespan(
        "Hvad tid gryr dagen her til morgen i dag?", "da", ANCHOR)
    assert found.span.start.datetime().date() == datetime(2017, 6, 27).date()


@pytest.mark.xfail(raises=AssertionError, strict=True, reason=ISSUE)
def test_pl_przyszlego_lata_is_summer_of_the_next_year():
    found = extract_timespan("przyszłego lata", "pl", ANCHOR)
    assert (found.span.start.datetime(), found.span.end.datetime()) == (
        datetime(2018, 6, 1), datetime(2018, 9, 1))
