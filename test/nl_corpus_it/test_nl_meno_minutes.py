"""Italian "meno N" minutes-to-the-hour clock: general minute counts, not just
the quarter idiom.

"le dieci meno venti" == 10 minus 20 minutes == 09:40; the stated hour is the
one being approached and the minute count is subtracted from it, rolling the
hour back by one.  This is the same "ore meno <minuti>" convention Italian uses
for the quarter ("le dieci meno un quarto" == 09:45); the quarter is merely one
value of the general minute offset.

Source: Italian Wikipedia, "Ora (unita di misura)" / Accademia della Crusca on
telling the time ("le ... meno ..."), where any minute count -- not only the
quarter -- names minutes still to run before the coming hour.
"""
import pytest

from ._corpus import span, start, AstroDate


@pytest.mark.parametrize("text,h,mi", [
    ("le dieci meno venti", 9, 40),
    ("le dieci meno dieci", 9, 50),
    ("le tre meno venti", 2, 40),
    ("le nove meno cinque", 8, 55),
    ("alle dieci meno venti", 9, 40),
    ("le dodici meno venti", 11, 40),
])
def test_meno_minutes(text, h, mi):
    assert start(text) == AstroDate(2017, 6, 28, h, mi)


def test_meno_minutes_consumes_article():
    """The leading article "le" is part of the construction, not leftover."""
    from ._corpus import parse
    r = parse("le dieci meno dieci")
    assert r is not None
    assert r[1].strip() == ""


# --- regressions: the quarter/half idioms that already work stay byte-exact ---
@pytest.mark.parametrize("text,h,mi", [
    ("le dieci meno un quarto", 9, 45),
    ("alle quattro meno un quarto", 3, 45),
    ("le nove e mezza", 9, 30),
    ("alle tre e un quarto", 3, 15),
])
def test_quarter_half_regressions(text, h, mi):
    assert start(text) == AstroDate(2017, 6, 28, h, mi)
