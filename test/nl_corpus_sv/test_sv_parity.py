"""sv: semantic-parity block -- each phrase resolves to the SAME span as
its English staple (same anchor).  Half-trap clock TIMES are excluded (they
diverge by design) in favour of phrasings invariant across the two languages.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

PAIRS = [('today', 'idag'), ('yesterday', 'igår'), ('tomorrow', 'imorgon'), ('overmorrow', 'övermorgon'), ('three days ago', 'för tre dagar sedan'), ('in three days', 'om tre dagar'), ('two weeks ago', 'för två veckor sedan'), ('in ten years', 'om tio år'), ('next monday', 'nästa måndag'), ('last friday', 'förra fredagen'), ('october 2020', 'oktober 2020'), ('march 1999', 'mars 1999'), ('the year 1969', 'år 1969'), ('1969', '1969'), ('44 bc', '44 före kristus'), ('753 bc', '753 före kristus'), ('2024 ad', '2024 efter kristus'), ('66 million years ago', 'för 66 miljoner år sedan'), ('summer 2020', 'sommar 2020'), ('next summer', 'nästa sommar'), ('spring 2021', 'vår 2021'), ('the third century', 'det tredje århundradet'), ('the 21st century', 'det 21 århundradet'), ('the first half of 2020', 'första hälften av 2020'), ('2019-03-15', '2019-03-15'), ('15:30', '15:30'), ('midnight', 'midnatt'), ('noon', 'middag'), ('quarter past three', 'kvart över tre'), ('from june 5th to june 12th', 'från 5 juni till 12 juni')]


@pytest.mark.parametrize("en_text,xx_text", PAIRS)
def test_parity(en_text, xx_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    xx = extract_timespan(xx_text, "sv", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert xx is not None, f"{xx_text!r} did not parse"
    assert xx[0].start == en[0].start, f"{xx_text!r} vs {en_text!r} start"
    assert xx[0].end == en[0].end, f"{xx_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 30
