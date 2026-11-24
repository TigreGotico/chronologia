"""A bare month after "since" reads alike in extract_timespan and
extract_candidates.

Alone, "january" names its next occurrence.  After "since" it names the one
that has begun, and extract_timespan answers with it.  The top candidate is
that same answer.  Under a range the month is one end of the range and keeps
its plain reading: it "da" is both "from" and "since", and the January of
"da gennaio a marzo" is the January the range starts in.

Anchor 2026-11-22 09:00: the January that has begun is January 2026, the next
one is January 2027.
"""
from datetime import datetime

from chronologia import extract_candidates, extract_timespan
from chronologia.astrodate import AstroDate, DateSpan

ANCHOR = datetime(2026, 11, 22, 9, 0)
JANUARY_2026 = DateSpan(AstroDate(2026, 1, 1), AstroDate(2026, 2, 1))


def test_top_candidate_is_the_timespan_answer_after_since():
    text = "ever since january we met"
    span, rest = extract_timespan(text, "en", ANCHOR)
    assert (span.start, span.end) == (JANUARY_2026.start, JANUARY_2026.end)
    top = extract_candidates(text, "en", ANCHOR)[0]
    assert (top.span.start, top.span.end, top.remainder) == (
        span.start, span.end, rest)


def test_month_under_a_range_keeps_its_plain_reading():
    found = extract_candidates("da gennaio a marzo", "it", ANCHOR)
    assert found[0].construction == "date_range"
    january = [c for c in found if c.remainder == "da a marzo"]
    assert [c.span.start for c in january] == [found[0].span.start]
    assert found[0].span.start == AstroDate(2027, 1, 1)
