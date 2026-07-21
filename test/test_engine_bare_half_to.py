"""Engine facts added for the Continental-Germanic languages, tested at the
engine level (independent of any one locale's full corpus):

* ``conventions.bare_half_to`` -- a bare half-fraction with no direction word
  counts DOWN to the stated hour ("halb neun" == 08:30), and ONLY the half
  fraction takes this form (a bare quarter is rejected);
* multi-word connectors -- a connector surface may span several tokens
  ("vor christus", "v. chr."), matched word-for-word;
* localized range connectives -- "von A bis B" resolves from the locale's
  own from/to/between/and connectors (dev's range mechanism).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.extract import load_lang_spec

ANCHOR = datetime(2017, 6, 27, 13, 4)


def test_bare_half_to_is_a_fact_on_de():
    assert load_lang_spec("de").conventions.bare_half_to is True


def test_en_does_not_have_bare_half_to():
    assert load_lang_spec("en").conventions.bare_half_to is False


@pytest.mark.parametrize("text,hour,minute", [
    ("halb neun", 8, 30), ("halb eins", 0, 30), ("halb mittag", 11, 30),
])
def test_bare_half_counts_down(text, hour, minute):
    s = extract_timespan(text, "de", ANCHOR)[0].start
    assert (s.hour, s.minute) == (hour, minute)


def test_english_half_nine_stays_half_past():
    # the opposite convention still holds for English (unchanged)
    s = extract_timespan("half past nine", "en", ANCHOR)[0].start
    assert (s.hour, s.minute) == (9, 30)


def test_bare_quarter_is_rejected():
    # only the half fraction takes the bare-to form
    assert extract_timespan("viertel neun", "de", ANCHOR) is None


def test_multiword_connector_bc():
    # "vor christus" is a two-token connector surface
    assert extract_timespan("44 vor christus", "de", ANCHOR)[0].start.year == -43
    assert extract_timespan("44 v. chr.", "de", ANCHOR)[0].start.year == -43


def test_localized_range_von_bis():
    s, _ = extract_timespan("von 1990 bis 2000", "de", ANCHOR)
    assert s.start.year == 1990 and s.end.year == 2001
