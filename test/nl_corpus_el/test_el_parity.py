"""Semantic-parity block: a Greek phrase must resolve to the SAME span as
its English staple (same anchor).  The engine core is shared, so equivalent
phrasings must land identically.

Clock times that diverge idiomatically are asserted in test_el_clock.py; the
entries below use phrasings invariant across the two languages (digit times,
landmarks, "και τέταρτο" == "quarter past").
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: (english, greek) -- must produce identical spans.
PAIRS = [
    # rel_period / weekend / bare-weekday rollout
    ('next week', 'επόμενη εβδομάδα'),
    ('this weekend', 'το σαββατοκύριακο'),
    ('friday', 'παρασκευή'),
    ("today", "σήμερα"),
    ("yesterday", "χθες"),
    ("tomorrow", "αύριο"),
    ("overmorrow", "μεθαύριο"),
    ("three days ago", "πριν 3 μέρες"),
    ("in three days", "σε 3 μέρες"),
    ("two weeks ago", "πριν δύο εβδομάδες"),
    ("in ten years", "σε δέκα χρόνια"),
    ("five months ago", "πριν πέντε μήνες"),
    ("in one hour", "σε μία ώρα"),
    ("30 minutes ago", "πριν 30 λεπτά"),
    ("next tuesday", "επόμενη τρίτη"),
    ("next monday", "επόμενη δευτέρα"),
    ("last friday", "προηγούμενη παρασκευή"),
    ("october 2020", "οκτώβριος 2020"),
    ("march 1999", "μάρτιος 1999"),
    ("the year 1969", "το έτος 1969"),
    ("1969", "1969"),
    ("2000", "2000"),
    ("44 bc", "44 π.χ."),
    ("753 bc", "753 π.χ."),
    ("2024 ad", "2024 μ.χ."),
    ("66 million years ago", "πριν από 66 εκατομμύρια χρόνια"),
    ("summer 2020", "καλοκαίρι 2020"),
    ("spring 2021", "άνοιξη 2021"),
    ("winter 2020", "χειμώνας 2020"),
    ("2019-03-15", "2019-03-15"),
    ("15:30", "15:30"),
    ("midnight", "μεσάνυχτα"),
    ("noon", "μεσημέρι"),
]


@pytest.mark.parametrize("en_text,el_text", PAIRS)
def test_parity(en_text, el_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    el = extract_timespan(el_text, "el", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert el is not None, f"greek {el_text!r} did not parse"
    assert el[0].start == en[0].start, f"{el_text!r} vs {en_text!r} start"
    assert el[0].end == en[0].end, f"{el_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 25
