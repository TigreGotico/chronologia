"""Polish weekday nouns in the instrumental case: "między środą a piątkiem"
(between Wednesday and Friday) -- "między ... a ..." governs the instrumental,
the one case ``weekday_N.voc`` never shipped, so the "between" range's own
sub-parse of each endpoint had nothing to bind and the whole range stranded.
The genitive counterpart ("od środy do piątku") already worked, proving the
range machinery itself was never the problem -- only the missing case form.
Expected dates are hand-counted from the anchor Monday (2026-06-15),
independent of the parser.
"""
from datetime import datetime

from chronologia.astrodate import AstroDate
from ._corpus import start_end

ANCHOR = datetime(2026, 6, 15, 12, 0)


def test_between_instrumental_weekdays():
    s, e = start_end("między środą a piątkiem", anchor=ANCHOR)
    assert s == AstroDate(2026, 6, 17)
    assert e == AstroDate(2026, 6, 20)


def test_between_instrumental_matches_genitive_from_to():
    assert start_end("między środą a piątkiem", anchor=ANCHOR) == \
        start_end("od środy do piątku", anchor=ANCHOR)
