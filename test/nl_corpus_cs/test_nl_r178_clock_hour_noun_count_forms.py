"""cs: a small clock hour (spoken or digit) must consume the "hodiny"
[hodina]" hour-noun count form (2-4) and the "hodinu" accusative-singular
form (1) after it, not strand the noun in the remainder.  Czech counts the
hour noun by grammatical number -- singular "hodinu" after one, the count
plural "hodiny" after two to four, the genitive plural "hodin" from five up
-- and all three must fold into the CLOCK construction the same way the
digit clock already consumes "hodin" ("v 9 hodin").
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse


@pytest.mark.parametrize("text,hour", [
    ("v 1 hodinu", 1),
    ("v 2 hodiny", 2),
    ("v 4 hodiny", 4),
    ("ve dvě hodiny", 2),
    ("ve čtyři hodiny", 4),
])
def test_small_hour_consumes_count_form(text, hour):
    r = parse(text)
    assert r is not None
    # ANCHOR is 2017-06-27 13:04; every clock hour 1..12 read as 24h is
    # earlier in the day than the anchor's time-of-day, so it rolls forward
    # to the next calendar day.
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=hour, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
