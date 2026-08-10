"""Regression: TimeMention.char_span must cover the full surface text,
including an English ordinal suffix (st/nd/rd/th) merged onto the digits by
the numfold pre-pass.

Bug (verified on dev f73cca4a, lang en, anchor 2026-08-10 09:00):
``extract_timespans('the reception on the 6th')`` returns a mention with
``.text == 'on the 6th'`` but ``.char_span == (14, 22)``, which slices the
sentence to ``'on the 6'`` -- the trailing ``th`` falls outside the span even
though it is part of the matched surface text. The corruption is silent and
propagates: when a NON-selected mention is removed from the sentence by its
(short) char_span in ``extract_timespan``, the ordinal suffix survives in the
remainder and turns 'the 6th' into 'the 6' -- a meaning-changing edit.
"""
from datetime import datetime

from chronologia import extract_timespan, extract_timespans

ANCHOR = datetime(2026, 8, 10, 9, 0)


def _assert_spans_agree(sentence, lang="en"):
    mentions = extract_timespans(sentence, lang=lang, anchor=ANCHOR)
    assert mentions, f"no mentions extracted from {sentence!r}"
    for m in mentions:
        assert m.char_span is not None, f"missing char_span for {m.text!r}"
        start, end = m.char_span
        got = sentence[start:end]
        assert got == m.text, (
            f"char_span {m.char_span} slices to {got!r}, "
            f"but mention.text is {m.text!r} (sentence={sentence!r})"
        )


def test_charspan_ordinal_mid_sentence():
    _assert_spans_agree("the reception on the 6th is confirmed")


def test_charspan_ordinal_sentence_final():
    _assert_spans_agree("the reception on the 6th")


def test_charspan_ordinal_21st():
    _assert_spans_agree("we depart on the 21st")


def test_charspan_ordinal_22nd():
    _assert_spans_agree("we depart on the 22nd")


def test_charspan_ordinal_3rd():
    _assert_spans_agree("we depart on the 3rd of the month")


def test_charspan_non_ordinal_control():
    _assert_spans_agree("meet me tomorrow")
    _assert_spans_agree("the meeting is on june 6")


def test_extract_timespan_remainder_keeps_ordinal_suffix_intact():
    """The non-selected mention must be stripped from the remainder using its
    FULL span, so the ordinal suffix of the other mention is never silently
    turned into a cardinal number."""
    result = extract_timespan(
        "meet on june 1st and also on the 6th", lang="en", anchor=ANCHOR
    )
    assert "the 6th" in result.remainder
    assert "the 6 " not in result.remainder
    assert not result.remainder.rstrip().endswith("the 6")
