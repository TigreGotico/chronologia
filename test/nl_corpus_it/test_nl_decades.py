"""Italian decade references: "gli anni ottanta".

Italian names a decade with the plural "anni" plus the bare tens numeral --
Treccani's grammar answer on the spelling of decades takes "gli anni Sessanta"
as the form, "con ellissi del nome anni, i Sessanta" -- so the numeral alone
is just a number and it is the framing "anni" that makes it a decade.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y0", [
    ("gli anni ottanta", 1980),
    ("gli anni novanta", 1990),
    ("gli anni venti", 1920),
    ("negli anni settanta", 1970),
    ("gli anni 80", 1980),
    ("gli anni 1980", 1980),
])
def test_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_decade_is_ten_years_wide():
    assert span("gli anni ottanta").width == timedelta(days=3653)


def test_bare_cardinal_is_still_a_number():
    # "ottanta" on its own is the number eighty, not the eighties
    nomatch("ottanta euro")


def test_bare_year_is_still_a_year():
    assert start_end("nel 1980") == (AstroDate(1980, 1, 1),
                                     AstroDate(1981, 1, 1))


def test_garbage_does_not_raise():
    nomatch("gli anni ???")
