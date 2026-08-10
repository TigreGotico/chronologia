"""Character offsets on every extracted mention.

:func:`~chronologia.extract.extract_timespans` tags each ``TimeMention`` with a
``char_span`` -- a half-open ``(start, end)`` character range into the ORIGINAL
utterance, taken from the tokenizer's own recorded offsets (never recovered by
re-searching the string).  So ``utterance[char_span[0]:char_span[1]]`` recovers
the exact substring the mention was read from, even after spelled-number
folding and multi-word merges rewrote the token text.
"""
from datetime import datetime

import pytest

from chronologia.extract.nseries import extract_timespans

ANCHOR = datetime(2017, 6, 27, 13, 4)


# (utterance, expected substring for each mention, in reading order)
_CASES = [
    ("meet on 2026-07-05", ["2026-07-05"]),
    ("the deadline is june 5th 2027", ["june 5th 2027"]),
    ("call me at 3pm", ["at 3pm"]),
    # R90: calendar_date's "DAY of MONTH..." order now carries a leading
    # article? (it was silently stranding "the" before), so the recovered
    # char span grows to cover the article too -- same date, wider match.
    ("the fifth of june", ["the fifth of june"]),
    ("Q3 2026 is busy", ["q3 2026"]),
    ("see the report by week 32", ["week 32"]),
    ("early next week works", ["early next week"]),
    ("meeting at 3pm utc", ["at 3pm utc"]),
    ("in 2019 we shipped", ["in 2019"]),
    ("next friday", ["next friday"]),
]


@pytest.mark.parametrize("utterance,wants", _CASES)
def test_char_offsets_recover_substring(utterance, wants):
    mentions = extract_timespans(utterance, "en", anchor=ANCHOR)
    assert len(mentions) == len(wants), \
        f"{utterance!r} -> {[m.text for m in mentions]}"
    lowered = utterance.lower()
    for m, want in zip(mentions, wants):
        assert m.char_span is not None
        cs, ce = m.char_span
        assert lowered[cs:ce] == want
        # the token_span and char_span agree on ordering / non-emptiness
        assert cs < ce


def test_two_mentions_have_disjoint_ordered_offsets():
    u = "meet friday at 3 or monday at noon"
    mentions = extract_timespans(u, "en", anchor=ANCHOR)
    assert len(mentions) == 2
    (a, b) = mentions
    assert a.char_span[1] <= b.char_span[0]     # non-overlapping, in order
    assert u.lower()[a.char_span[0]:a.char_span[1]].startswith("friday")


def test_no_mention_yields_empty_list():
    assert extract_timespans("just some ordinary words", "en",
                             anchor=ANCHOR) == []
