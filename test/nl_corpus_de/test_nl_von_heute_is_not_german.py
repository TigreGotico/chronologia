"""The "N <unit> von heute" rows are a translation artifact, not German.

ovos-date-parser's German corpus carries "setze den frisörtermin auf 5 tage
von heute" and "spiele happy birthday musik 5 jahre von heute", rendering
the English "N days from today" word for word.  German does not build a
counted offset that way: de.wikipedia has no hit at all for "Tage von
heute", while "Tage ab" and "Wochen ab" run to dozens in exactly that sense
("16 Wochen ab dem ersten Tag der letzten Menstruation", "568 Tage ab dem
31. Oktober 1795").  Bare "von heute" means *of* today -- die Zeitung von
heute -- and the idiomatic forward frame is "von heute an".

These rows are therefore pinned as an artifact rather than closed as a gap.
No date is asserted: the point is that the phrase carries no German reading
to be right or wrong about, and pinning a value would invent one.  The
attested frame is covered separately and resolves.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text", [
    "setze den frisörtermin auf 5 tage von heute",
    "spiele happy birthday musik 5 jahre von heute",
    "5 tage von heute",
])
def test_the_calqued_frame_yields_no_counted_offset(text):
    """The count must not be consumed: whatever resolves, it is not N from today.

    Asserted as "the counted offset is not read", not as a date, so the pin
    cannot drift into claiming a value for a phrase German does not build.
    """
    r = parse(text)
    if r is not None:
        assert "von" in r.remainder, (
            f"{text!r} consumed the calqued offset frame: {r!r}"
        )


@pytest.mark.parametrize("text,day", [
    # the attested German frame, which does resolve
    ("2 wochen ab samstag", 15),
])
def test_the_attested_ab_frame_resolves(text, day):
    got = start(text)
    assert (got.year, got.month, got.day) == (2017, 7, day)
