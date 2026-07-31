"""Direct unit coverage for TransitionRule (the year-segmented holiday kind).

Reached end-to-end via the uk Christmas corpus, but the class's own contract --
latest-segment-at-or-before-year, honest silence before the first segment, and
ascending/unique-year validation -- was otherwise untested.
"""
import pytest

from chronologia.civil_holidays.rules import (CalendarDateRule, FixedRule,
                                              TransitionRule)


def test_transition_rule_picks_latest_segment_at_or_before_year():
    r = TransitionRule(((2000, FixedRule(1, 1)),
                        (2010, FixedRule(6, 15)),
                        (2020, FixedRule(12, 31))))
    assert r.observances(2005) == FixedRule(1, 1).observances(2005)
    assert r.observances(2010) == FixedRule(6, 15).observances(2010)   # boundary
    assert r.observances(2019) == FixedRule(6, 15).observances(2019)
    assert r.observances(2020) == FixedRule(12, 31).observances(2020)  # boundary
    assert r.observances(2025) == FixedRule(12, 31).observances(2025)


def test_transition_rule_silent_before_first_segment():
    r = TransitionRule(((2010, FixedRule(1, 1)),))
    assert r.observances(2005) == ()          # honest silence, not a fabricated date


def test_transition_rule_ukraine_christmas_shape():
    # the shipped shape: Julian (civil Jan 7) through 2022, Gregorian Dec 25 from 2023
    r = TransitionRule(((1, CalendarDateRule("julian", 12, 25)),
                        (2023, FixedRule(12, 25))))
    (d2022, _), = r.observances(2022)
    (d2023, _), = r.observances(2023)
    assert (d2022.month, d2022.day) == (1, 7)     # Julian Dec 25 -> civil Jan 7
    assert (d2023.month, d2023.day) == (12, 25)


def test_transition_rule_rejects_empty_or_unsorted_segments():
    with pytest.raises(ValueError):
        TransitionRule(())
    with pytest.raises(ValueError):
        TransitionRule(((2010, FixedRule(1, 1)), (2000, FixedRule(1, 1))))  # not ascending
    with pytest.raises(ValueError):
        TransitionRule(((2010, FixedRule(1, 1)), (2010, FixedRule(2, 2))))  # duplicate year
