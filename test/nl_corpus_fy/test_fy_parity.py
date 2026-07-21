"""fy: semantic-parity block -- each phrase resolves to the SAME span as
its English staple (same anchor).  Half-trap clock TIMES are excluded (they
diverge by design) in favour of phrasings invariant across the two languages.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

PAIRS = [('today', 'hjoed'), ('yesterday', 'juster'), ('tomorrow', 'moarn'), ('overmorrow', 'oaremoarn'), ('three days ago', 'trije dagen lyn'), ('in three days', 'oer trije dagen'), ('two weeks ago', 'twa wiken lyn'), ('in ten years', 'oer tsien jier'), ('next monday', 'oare moandei'), ('last friday', 'ôfrûne freed'), ('october 2020', 'oktober 2020'), ('march 1999', 'maart 1999'), ('the year 1969', 'it jier 1969'), ('1969', '1969'), ('44 bc', '44 foar kristus'), ('753 bc', '753 foar kristus'), ('2024 ad', '2024 nei kristus'), ('66 million years ago', '66 miljoen jier lyn'), ('summer 2020', 'simmer 2020'), ('next summer', 'oare simmer'), ('spring 2021', 'maitiid 2021'), ('the third century', 'de tredde ieu'), ('the 21st century', 'de 21e ieu'), ('the first half of 2020', 'de earste helte fan 2020'), ('2019-03-15', '2019-03-15'), ('15:30', '15:30'), ('midnight', 'middernacht'), ('noon', 'middei'), ('quarter past four', 'kertier oer fjouweren'), ('from june 5th to june 12th', 'fan 5 juny oant 12 juny')]


@pytest.mark.parametrize("en_text,xx_text", PAIRS)
def test_parity(en_text, xx_text):
    en = extract_timespan(en_text, "en", ANCHOR)
    xx = extract_timespan(xx_text, "fy", ANCHOR)
    assert en is not None, f"english staple {en_text!r} did not parse"
    assert xx is not None, f"{xx_text!r} did not parse"
    assert xx[0].start == en[0].start, f"{xx_text!r} vs {en_text!r} start"
    assert xx[0].end == en[0].end, f"{xx_text!r} vs {en_text!r} end"


def test_parity_block_size():
    assert len(PAIRS) >= 30
