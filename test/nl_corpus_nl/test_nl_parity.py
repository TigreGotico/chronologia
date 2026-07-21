"""nl: semantic-parity block -- each phrase resolves to the SAME span as
its English staple (same anchor).  Half-trap clock TIMES are excluded (they
diverge by design) in favour of phrasings invariant across the two languages.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

PAIRS = [('today', 'vandaag'), ('yesterday', 'gisteren'), ('tomorrow', 'morgen'), ('overmorrow', 'overmorgen'), ('three days ago', 'drie dagen geleden'), ('in three days', 'over drie dagen'), ('two weeks ago', 'twee weken geleden'), ('in ten years', 'over tien jaar'), ('next monday', 'volgende maandag'), ('last friday', 'vorige vrijdag'), ('october 2020', 'oktober 2020'), ('march 1999', 'maart 1999'), ('the year 1969', 'het jaar 1969'), ('1969', '1969'), ('44 bc', '44 voor christus'), ('753 bc', '753 voor christus'), ('2024 ad', '2024 na christus'), ('66 million years ago', '66 miljoen jaar geleden'), ('summer 2020', 'zomer 2020'), ('next summer', 'volgende zomer'), ('spring 2021', 'lente 2021'), ('the third century', 'de derde eeuw'), ('the 21st century', 'de 21e eeuw'), ('the first half of 2020', 'de eerste helft van 2020'), ('2019-03-15', '2019-03-15'), ('15:30', '15:30'), ('midnight', 'middernacht'), ('noon', 'middag'), ('quarter past three', 'kwart over drie'), ('from june 5th to june 12th', 'van 5 juni tot 12 juni')]


@pytest.mark.parametrize("en_text,xx_text", PAIRS)
def test_parity(en_text, xx_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    xx = extract_timespan(xx_text, "nl", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert xx is not None, f"{xx_text!r} did not parse"
    assert xx[0].start == en[0].start, f"{xx_text!r} vs {en_text!r} start"
    assert xx[0].end == en[0].end, f"{xx_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 30
