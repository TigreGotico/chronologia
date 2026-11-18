"""A bare "after"/"before" before a date that takes "the".

"after may 13" is the open span from the end of 13 May onward, with no end.
"after the 13th of may" is the same reference with an article, so it reads
the same, not as 13 May with "after" left over.
"before the 13th of may" is the range from now to the start of 13 May, as
"before may 13" is (ruling 29: "before X" ends when X begins).  Anchor 16 November 2026: the next 13 May is in 2027.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

from ._corpus import parse

ANCHOR = datetime(2026, 11, 16, 12, 0)


@pytest.mark.parametrize("text", [
    "after may 13",
    "after the 13th of may",
])
def test_after_the_date_is_open_from_its_end(text):
    span, rest = parse(text, ANCHOR)
    assert (span.start, span.open_end) == (datetime(2027, 5, 14), True)
    assert rest == ""


@pytest.mark.parametrize("text", ["before may 13", "before the 13th of may"])
def test_before_the_date_runs_from_now_to_its_start(text):
    span, rest = parse(text, ANCHOR)
    assert (span.start, span.end) == (ANCHOR, datetime(2027, 5, 13))
    assert rest == ""


@pytest.mark.parametrize("lang, text", [
    # controls: a connector between the marker and the date that the date
    # does not read stays with the marker
    ("es", "antes del 13 de mayo"),
    ("de", "vor dem 13. Mai"),
])
def test_before_with_a_connector_leaves_nothing(lang, text):
    span, rest = extract_timespan(text, lang, ANCHOR)
    assert (span.start, span.end) == (ANCHOR, datetime(2027, 5, 13))
    assert rest == ""
