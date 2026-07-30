"""The negation/exclusion safety guard is per-locale data, not English-only.

A bare reference governed by a leading negation particle ("not tomorrow") must
NOT be handed back as a positive date -- the residue-veto guard against acting on
an excluded day. This guard is driven by per-locale ``marker_exclusion`` /
``marker_exclusion_bound`` vocabularies; the languages below declare them, so the
guard holds for each, not just English.

Anchor: 2017-06-27 (a Tuesday); "tomorrow" resolves to 2017-06-28.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

_ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,lang", [
    ("not tomorrow", "en"),
    ("nicht morgen", "de"),
    ("pas demain", "fr"),
    ("non domani", "it"),
    ("não amanhã", "pt"),
])
def test_negated_reference_is_vetoed(text, lang):
    # the excluded day must not come back as a positive date
    assert extract_timespan(text, lang, _ANCHOR) is None


@pytest.mark.parametrize("text,lang", [
    ("tomorrow", "en"),
    ("morgen", "de"),
    ("demain", "fr"),
    ("domani", "it"),
    ("amanhã", "pt"),
])
def test_plain_reference_still_resolves(text, lang):
    result = extract_timespan(text, lang, _ANCHOR)
    assert result is not None
    assert result[0].start_datetime.date().isoformat() == "2017-06-28"


def test_bound_preposition_is_not_an_exclusion():
    # "no later than friday" is a bound, not an exclusion -- must still resolve
    result = extract_timespan("no later than friday", "en", _ANCHOR)
    assert result is not None
    assert result[0].start_datetime.date().isoformat() == "2017-06-30"


def test_unpopulated_locale_guard_is_a_noop():
    # a locale that declares no exclusion vocab keeps its prior behaviour (the
    # guard never silently applies English particles): "ru" has none, so a bare
    # weekday still resolves rather than being vetoed by a foreign trigger.
    result = extract_timespan("завтра", "ru", _ANCHOR)  # "tomorrow"
    assert result is not None
    assert result[0].start_datetime.date().isoformat() == "2017-06-28"
