"""Romanian clock: "la ora N", "ora N", the "si un sfert" / "fara un sfert"
/ "si jumatate" fraction system, dimineata / seara meridiems, amiaza."""
from datetime import timedelta

import pytest

from ._corpus import span, start, AstroDate


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    ("ora 20", 2017, 6, 27, 20, 0),
    ("7 seara", 2017, 6, 27, 19, 0),
    ("la ora trei", 2017, 6, 28, 3, 0),
    ("la ora 3", 2017, 6, 28, 3, 0),
    ("3 dimineața", 2017, 6, 28, 3, 0),
    ("la amiază", 2017, 6, 28, 12, 0),
    ("trei și un sfert", 2017, 6, 28, 3, 15),
    ("nouă și jumătate", 2017, 6, 28, 9, 30),
    ("patru fără un sfert", 2017, 6, 28, 3, 45),
    ("opt și un sfert", 2017, 6, 28, 8, 15),
    ("trei și jumătate", 2017, 6, 28, 3, 30),
])
def test_clock(text, y, mo, d, h, mi):
    assert start(text) == AstroDate(y, mo, d, h, mi)


def test_clock_is_minute_wide():
    assert span("trei și un sfert").width == timedelta(minutes=1)


def test_fara_un_sfert_not_a_range():
    assert start("patru fără un sfert") == AstroDate(2017, 6, 28, 3, 45)


def test_gibberish_no_crash():
    from ._corpus import parse
    for tok in ["10iul", "7z", "20h99z"]:
        parse(tok)
