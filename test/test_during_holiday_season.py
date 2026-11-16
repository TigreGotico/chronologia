"""The base "in"/"during" slots before a season or a holiday, in other
locales.  Meteorological summer is June, July and August (NOAA NCEI,
"Meteorological Versus Astronomical Seasons").  Anchor 16 November 2026."""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 16, 12, 0)
SUMMER_2027 = (datetime(2027, 6, 1), datetime(2027, 9, 1))


@pytest.mark.parametrize("lang, text, bounds", [
    ("fr", "pendant noël", (datetime(2026, 12, 25), datetime(2026, 12, 26))),
    ("fr", "pendant l'été 2027", SUMMER_2027),
    ("es", "durante el verano de 2027", SUMMER_2027),
    ("es", "durante la navidad", (datetime(2026, 12, 25),
                                  datetime(2026, 12, 26))),
    ("de", "während Weihnachten", (datetime(2026, 12, 25),
                                   datetime(2026, 12, 26))),
])
def test_during_reads_with_the_reference(lang, text, bounds):
    span, rest = extract_timespan(text, lang, anchor=ANCHOR)
    assert (span.start, span.end) == bounds
    assert rest == ""
