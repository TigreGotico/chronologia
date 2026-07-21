"""da: semantic-parity block -- each phrase resolves to the SAME span as
its English staple (same anchor).  Half-trap clock TIMES are excluded (they
diverge by design) in favour of phrasings invariant across the two languages.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

PAIRS = [('today', 'idag'), ('yesterday', 'igår'), ('tomorrow', 'imorgen'), ('overmorrow', 'overmorgen'), ('three days ago', 'for tre dage siden'), ('in three days', 'om tre dage'), ('two weeks ago', 'for to uger siden'), ('in ten years', 'om ti år'), ('next monday', 'næste mandag'), ('last friday', 'sidste fredag'), ('october 2020', 'oktober 2020'), ('march 1999', 'marts 1999'), ('the year 1969', 'år 1969'), ('1969', '1969'), ('44 bc', '44 før kristus'), ('753 bc', '753 før kristus'), ('2024 ad', '2024 efter kristus'), ('66 million years ago', 'for 66 millioner år siden'), ('summer 2020', 'sommer 2020'), ('next summer', 'næste sommer'), ('the 21st century', 'det 21. århundrede'), ('the first half of 2020', '1. halvdel af 2020'), ('2019-03-15', '2019-03-15'), ('15:30', '15:30'), ('midnight', 'midnat'), ('noon', 'middag'), ('quarter past three', 'kvart over tre'), ('from june 5th to june 12th', 'fra 5. juni til 12. juni'), ('the third century', 'det 3. århundrede'), ('in ten days', 'om ti dage'), ('6 june 1944', '6. juni 1944')]


@pytest.mark.parametrize("en_text,xx_text", PAIRS)
def test_parity(en_text, xx_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    xx = extract_timespan(xx_text, "da", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert xx is not None, f"{xx_text!r} did not parse"
    assert xx[0].start == en[0].start, f"{xx_text!r} vs {en_text!r} start"
    assert xx[0].end == en[0].end, f"{xx_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 30
