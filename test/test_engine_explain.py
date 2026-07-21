"""Explain window: winners with bindings + resolved value, and losers
with a reason naming the rival that beat them."""
from engine_helpers import ANCHOR, load_zz

from chronologia.extract import explain


def test_winner_reports_binding_and_value():
    trace = explain("3 zdays zhence", load_zz(), ANCHOR)
    assert len(trace.winners) == 1
    won = trace.winners[0]
    assert won.match.construction == "relative_offset"
    assert won.match.slots["NUM"].text == "3"
    assert won.resolution.value is not None
    assert "relative_offset" in trace.report()


def test_losers_have_reasons_for_subsumed_spans():
    # "5 zof zjun 2027" matches the DMY order over (0,4); the trailing
    # "zjun 2027" also matches the MDY order over (2,4), which must lose.
    trace = explain("5 zof zjun 2027", load_zz(), ANCHOR)
    assert trace.winners[0].match.span == (0, 4)
    assert trace.losers, "expected an overlapping shorter candidate as loser"
    assert any("longer" in lost.reason for lost in trace.losers)


def test_report_is_stringable_for_empty_text():
    trace = explain("", load_zz(), ANCHOR)
    assert trace.winners == () and str(trace)


def test_report_lists_tokens():
    trace = explain("zmorrow", load_zz(), ANCHOR)
    assert "zmorrow" in trace.report()
