"""Negated / excluded temporal references must veto to None.

A reference governed by a negation/exclusion particle ("not tomorrow", "any
day but Friday", "except Sundays") is NOT a positive date.  Resolving it
positively hands back the exact day the user told us to avoid -- an inverted,
hazardous result (a scheduler would book the excluded day).  Per the
residue-veto design (docs/design/errors-by-construction.md, #244), such a
reference returns None.

A BOUND phrase ("not before Monday", "no later than Friday") is a legitimately
resolvable constraint, NOT an exclusion, and is left byte-identical.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.extract import extract_candidates
from chronologia.extract.nseries import extract_timespans

# Tuesday 2017-06-27 13:04.
ANCHOR = datetime(2017, 6, 27, 13, 4)


# --- exclusions: the excluded reference is not a positive date -> None -------
@pytest.mark.parametrize("text", [
    "not tomorrow",
    "not this Friday",
    "not next week",
    "any day but Friday",
    "anything but Monday",
    "unless it is Tuesday",
    "not on weekends",
    "except Sundays",
    "except on Friday",
    "other than Monday",
    "no weekends",
])
def test_negated_reference_vetoes_to_none(text):
    assert extract_timespan(text, "en", ANCHOR) is None


@pytest.mark.parametrize("text", [
    "not tomorrow",
    "any day but Friday",
    "except on Friday",
    "no weekends",
])
def test_negated_reference_empty_in_timespans_and_candidates(text):
    assert extract_timespans(text, "en", ANCHOR) == []
    assert extract_candidates(text, "en", ANCHOR) == []


# --- bounds: legitimately resolvable, left unchanged (regression pins) -------
# Each value is the CURRENT dev behaviour recorded verbatim.
@pytest.mark.parametrize("text,start,end,rem", [
    ("not before Monday", "2017-07-03T00:00:00", "2017-07-04T00:00:00", "not before"),
    ("no earlier than 5pm", "2017-06-27T17:00:00", "2017-06-27T17:01:00", "no earlier than"),
    ("no later than Friday", "2017-06-30T00:00:00", "2017-07-01T00:00:00", "no later than"),
    ("not until Tuesday", "2017-07-04T00:00:00", "2017-07-05T00:00:00", "not until"),
    ("not after 3pm", "2017-06-27T15:00:00", "2017-06-27T15:01:00", "not after"),
    ("not before tomorrow", "2017-06-28T00:00:00", "2017-06-29T00:00:00", "not before"),
    ("not after Friday", "2017-06-30T00:00:00", "2017-07-01T00:00:00", "not after"),
])
def test_bound_phrases_unchanged(text, start, end, rem):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None
    assert str(r.span.start) == start
    assert str(r.span.end) == end
    assert r.remainder == rem


# --- plain references: no negation, unchanged -------------------------------
@pytest.mark.parametrize("text,start,end,rem", [
    ("tomorrow", "2017-06-28T00:00:00", "2017-06-29T00:00:00", ""),
    ("this Friday", "2017-06-30T00:00:00", "2017-07-01T00:00:00", ""),
    ("next week", "2017-07-03T00:00:00", "2017-07-10T00:00:00", ""),
    ("on weekends", "2017-07-01T00:00:00", "2017-07-03T00:00:00", "on"),
])
def test_plain_references_unchanged(text, start, end, rem):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None
    assert str(r.span.start) == start
    assert str(r.span.end) == end
    assert r.remainder == rem


# --- adjacency: a trigger must GOVERN the reference to veto it ---------------
# A trigger lying in another clause or sentence, or separated by a content word,
# does NOT govern the date and must not veto it (the veto used to scan the whole
# prefix and falsely returned None). "next Tuesday" resolves to 2017-07-04.
@pytest.mark.parametrize("text", [
    "no wait, Tuesday",                     # "wait" (content) blocks "no"
    "But Tuesday works for me",             # discourse-opening "but", no scope
    "I have a meeting but Tuesday is free",  # "but" is a clause conjunction here
    "I have no idea if Tuesday works",       # "idea" (content) blocks "no"
    "No cats allowed. See you Tuesday.",     # trigger in a prior sentence
])
def test_non_governing_trigger_does_not_veto(text):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None
    assert r.span.start.date().isoformat() == "2017-07-04"
    # both public APIs must agree the reading survives
    assert extract_candidates(text, "en", ANCHOR) != []


# The adjacent-exclusion idiom still vetoes: "but"/"except" governed by a scope
# word ("every day but X", "any day except X"), and a trigger reachable across
# only function words ("unless it is Tuesday").
@pytest.mark.parametrize("text", [
    "every day but Tuesday",
    "any day except Sunday",
    "anything but Monday",
    "unless it is Tuesday",
])
def test_adjacent_exclusion_still_vetoes(text):
    assert extract_timespan(text, "en", ANCHOR) is None
    assert extract_candidates(text, "en", ANCHOR) == []
