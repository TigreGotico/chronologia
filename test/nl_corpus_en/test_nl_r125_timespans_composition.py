"""R125: ``extract_timespans`` (the multi-mention edge) must apply the SAME
per-clause composition machinery ``extract_timespan`` (the single-span edge)
applies -- weekday+daypart+clock merge, daypart-meridiem, "for <duration>"
extension -- instead of returning un-merged, mis-anchored fragments for each
matcher hit.

Before the fix, "next tuesday evening at 9 for 2 hours, then again next
friday at 5" split into FOUR loose mentions ('next tuesday' -> whole day,
'evening' -> TODAY 18:00-21:00, 'at 9' -> TOMORROW 09:00, 'next friday at 5'
-> 05:00, that one already merged) instead of the two a human reads: the
first clause composed into one 21:00-23:00 meeting, the second unchanged.

Expected values are independently hand-computed against the anchor
(Tuesday 2017-06-27 13:04, from ``_corpus.ANCHOR``), never read back from the
parser -- except where noted, where the assertion is that the multi-mention
edge reproduces EXACTLY the single-span edge's own (independently-tested,
see ``test_nl_r119_clock_for_duration.py`` and ``test_nl_clock_composition.py``)
reading for the same clause -- the two APIs must not disagree, which is the
literal contract this defect broke.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan, extract_timespans
from ._corpus import ANCHOR, ad

LANG = "en"


def mentions(text):
    return extract_timespans(text, LANG, ANCHOR)


# --- the repro: R125's own defect sentence ----------------------------------

def test_r125_repro_two_composed_mentions():
    s = ("We meet next tuesday evening at 9 for 2 hours, "
         "then again next friday at 5.")
    ms = mentions(s)
    assert len(ms) == 2


def test_r125_first_clause_matches_single_span_edge():
    # the first clause, read alone, is independently covered by R117/R119's
    # own tests; the multi-mention edge must reproduce that EXACT reading
    # rather than a narrower fragment.
    clause = "next tuesday evening at 9 for 2 hours"
    ms = mentions("We meet next tuesday evening at 9 for 2 hours, "
                  "then again next friday at 5.")
    assert ms[0].span == extract_timespan(clause, LANG, ANCHOR).span
    # hand-derived: next Tuesday from Tue 2017-06-27 is 2017-07-04;
    # evening + "at 9" composes to 21:00 (9pm), +2h duration -> 23:00.
    assert ms[0].span.start == ad(datetime(2017, 7, 4, 21, 0))
    assert ms[0].span.end == ad(datetime(2017, 7, 4, 23, 0))


def test_r125_second_clause_unchanged():
    ms = mentions("We meet next tuesday evening at 9 for 2 hours, "
                  "then again next friday at 5.")
    # hand-derived: next Friday from Tue 2017-06-27 is 2017-06-30, at 05:00.
    assert ms[1].span.start == ad(datetime(2017, 6, 30, 5, 0))
    assert ms[1].span.end == ad(datetime(2017, 6, 30, 5, 1))
    assert ms[1].text == "next friday at 5"


def test_r125_no_stray_connector_in_composed_text():
    # the composed first mention must not swallow the "then" that opens the
    # second clause -- a regression on the char/token extent, not the span.
    ms = mentions("We meet next tuesday evening at 9 for 2 hours, "
                  "then again next friday at 5.")
    assert "then" not in ms[0].text
    assert "again" not in ms[0].text


# --- three-event narrative: every clause composes independently ------------

def test_r125_three_event_narrative():
    s = ("Call me monday morning at 9, then tuesday afternoon at 3, "
         "then wednesday evening at 7.")
    ms = mentions(s)
    assert len(ms) == 3
    assert [m.span.start for m in ms] == [
        ad(datetime(2017, 7, 3, 9, 0)),
        ad(datetime(2017, 7, 4, 15, 0)),
        ad(datetime(2017, 6, 28, 19, 0)),
    ]
    assert [m.text for m in ms] == [
        "monday morning at 9", "tuesday afternoon at 3",
        "wednesday evening at 7",
    ]


def test_r125_three_event_matches_single_span_edge_per_clause():
    s = ("Call me monday morning at 9, then tuesday afternoon at 3, "
         "then wednesday evening at 7.")
    ms = mentions(s)
    clauses = ["monday morning at 9", "tuesday afternoon at 3",
               "wednesday evening at 7"]
    for m, clause in zip(ms, clauses):
        assert m.span == extract_timespan(clause, LANG, ANCHOR).span


# --- range + composed clause together ---------------------------------------

def test_r125_range_then_composed_clause():
    s = ("From june 5th to june 12th we will travel, then rest next monday "
         "morning at 9 for 1 hour.")
    ms = mentions(s)
    assert len(ms) == 2
    # range: both dates are past the anchor's month/day -> roll to 2018.
    assert ms[0].span.start == ad(datetime(2018, 6, 5))
    assert ms[0].span.end == ad(datetime(2018, 6, 13))
    # next Monday from Tue 2017-06-27 is 2017-07-03; 9am + 1h -> 10am.
    assert ms[1].span.start == ad(datetime(2017, 7, 3, 9, 0))
    assert ms[1].span.end == ad(datetime(2017, 7, 3, 10, 0))


# --- non-merge controls: genuinely separate mentions never fuse ------------

@pytest.mark.parametrize("text,count", [
    # "and" is a separator, not glue: two independent clock-on-date mentions.
    ("tomorrow at 9 and next friday at 5.", 2),
    # a comma is not glue either.
    ("monday at 9, friday at 5", 2),
    # "or" list of composed readings: still 2, none merge across the "or".
    ("meet friday morning at 9 or monday evening at 5", 2),
])
def test_r125_non_merge_controls(text, count):
    assert len(mentions(text)) == count


def test_r125_non_merge_control_values():
    ms = mentions("tomorrow at 9 and next friday at 5.")
    assert len(ms) == 2
    assert ms[0].span.start == ad(datetime(2017, 6, 28, 9, 0))
    assert ms[1].span.start == ad(datetime(2017, 6, 30, 5, 0))
    # neither mention's text bleeds into the connector or the other clause.
    assert ms[0].text == "tomorrow at 9"
    assert ms[1].text == "next friday at 5"


# --- ordering and non-overlap guarantees are preserved ----------------------

def test_r125_mentions_stay_ordered_and_non_overlapping():
    s = ("We meet next tuesday evening at 9 for 2 hours, "
         "then again next friday at 5.")
    ms = mentions(s)
    starts = [m.token_span[0] for m in ms]
    assert starts == sorted(starts)
    for a, b in zip(ms, ms[1:]):
        assert a.token_span[1] <= b.token_span[0]


# --- single-mention sentences are unchanged by the clustering pass ---------

@pytest.mark.parametrize("text,count", [
    ("just tomorrow", 1),
    ("call me on monday", 1),
    ("next monday at 9am for 2 hours", 1),
    ("nothing temporal here", 0),
])
def test_r125_single_mention_sentences_unchanged(text, count):
    assert len(mentions(text)) == count


def test_r125_single_mention_matches_single_span_edge():
    text = "next monday at 9am for 2 hours"
    ms = mentions(text)
    assert len(ms) == 1
    assert ms[0].span == extract_timespan(text, LANG, ANCHOR).span
