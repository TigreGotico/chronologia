"""explain() fidelity for English: the debug window replays the *identical*
pre-match pipeline as extract_timespan (spelled-number fold + multiword merge),
so a trace never misrepresents a real parse.

Guards the regression where explain() ran a bare tokenizer+normaliser without
the language's numfold hook and multiword merge: spelled numbers showed up
unbound and multiword periods were invisible in the trace even though the real
parse bound them.
"""
from datetime import datetime

import pytest

from chronologia.extract import explain, extract_timespan
from chronologia.extract.loader import load_lang_spec

SPEC = load_lang_spec("en")
ANCHOR = datetime(2027, 1, 1)


def _winner(text):
    trace = explain(text, SPEC, ANCHOR)
    won = [w for w in trace.winners if w.resolution is not None]
    assert won, f"{text!r}: expected a resolved winner in the trace"
    return trace, won


def test_spelled_number_is_folded_and_bound():
    # "the fifth of june": the spelled ordinal must be folded to a digit and
    # bind the calendar_date DAY slot (the bug left it an unbound word)
    trace, won = _winner("the fifth of june")
    assert "5" in trace.report()
    cal = [w for w in won if w.match.construction == "calendar_date"]
    assert cal, "calendar_date did not win over 'the fifth of june'"
    assert cal[0].match.slots["DAY"].text == "5"
    assert cal[0].match.slots["MONTH"].text == "june"


def test_multiword_period_is_merged_in_trace():
    # "bronze age" is one tokenizer-split surface merged back into one token;
    # the trace must show the merged token bound to the PERIOD slot
    trace, won = _winner("the late bronze age")
    assert "bronze age" in trace.report()
    named = [w for w in won if w.match.construction == "named_period"]
    assert named and named[0].match.slots["PERIOD"].text == "bronze age"


def test_scoped_bc_shows_in_trace():
    trace, won = _winner("the 3rd century bc")
    top = won[0]
    assert top.match.construction == "scoped_bc"
    assert top.resolution.value.start.year == -299


# -- explain and extract_timespan agree on winning construction + span -----

_AGREEMENT = [
    "the fifth of june",
    "june 5th 2027",
    "the third week of june",
    "the 21st century",
    "the 3rd century bc",
    "the 1st millennium bc",
    "2nd century ad",
    "the late bronze age",
    "next monday",
    "44 bc",
    "66 million years ago",
    "the nineties",
]


@pytest.mark.parametrize("text", _AGREEMENT)
def test_explain_agrees_with_extract(text):
    result = extract_timespan(text, "en", ANCHOR)
    assert result is not None, f"{text!r} did not parse"
    span = result[0]
    _, won = _winner(text)
    # the span extract_timespan returns must be exactly one winner's resolution
    spans = [w.resolution.value for w in won]
    assert span in spans, (
        f"{text!r}: extract span {span} not among explain winners {spans}")
