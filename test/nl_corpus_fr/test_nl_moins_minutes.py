"""French "moins N" minutes-to-the-hour clock: general minute counts, not just
the quarter idiom.

"dix heures moins dix" == 10 hours minus 10 minutes == 09:50; the stated hour
is the one being approached and the minute count is subtracted from it, rolling
the hour back by one.  This is the same "... heures moins ..." convention French
uses for the quarter ("dix heures moins le quart" == 09:45); the quarter is
merely one value of the general minute offset.

Source: French Wikipedia, "Heure" (lecture de l'heure), where any minute count
-- not only "le quart" -- names minutes still to run before the coming hour.
"""
import pytest

from ._corpus import span, start, AstroDate


@pytest.mark.parametrize("text,h,mi", [
    ("dix heures moins dix", 9, 50),
    ("onze heures moins vingt", 10, 40),
    ("neuf heures moins cinq", 8, 55),
    ("dix heures moins vingt", 9, 40),
])
def test_moins_minutes(text, h, mi):
    assert start(text) == AstroDate(2017, 6, 28, h, mi)


def test_moins_minutes_consumes_offset():
    """The "moins <N>" offset is part of the construction, not leftover."""
    from ._corpus import parse
    r = parse("dix heures moins dix")
    assert r is not None
    assert r[1].strip() == ""


# --- regressions: the quarter idiom that already works stays byte-exact ---
@pytest.mark.parametrize("text,h,mi", [
    ("dix heures moins le quart", 9, 45),
])
def test_quart_regressions(text, h, mi):
    assert start(text) == AstroDate(2017, 6, 28, h, mi)
