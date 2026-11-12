"""Ukrainian "о пів на <hour>": the clock preposition before a half.

"пів на третю" is 02:30 (half onto the third hour), and "о" leads it as it
leads any clock: "Рівно о пів до сьомої" (Kotsiubynsky, quoted in Б.
Антоненко-Давидович, "Як ми говоримо", section "Непорозуміння з часом").  The
"о" belongs to the clock, so it does not stay in the remainder.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour, minute):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=minute, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour,minute,remainder", [
    ("о пів на третю", 28, 2, 30, ""),
    ("о пів на третю дня", 27, 14, 30, ""),
    ("завтра о пів на восьму", 28, 7, 30, ""),
    ("зустрінемось о пів на дев'яту", 28, 8, 30, "зустрінемось"),
])
def test_o_before_half_clock(text, day, hour, minute, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour, minute)
    assert r.remainder == remainder
