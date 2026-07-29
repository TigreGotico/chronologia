# -*- coding: utf-8 -*-
"""Article-LESS worded quarter "cuarto trimestre de <year>" (4th quarter).

The article-borne form "el cuarto trimestre de <year>" already bound (the
definite article licenses the ordinal reading of the ordinal-fraction homograph
"cuarto", spelled like the clock quarter-hour fraction "un cuarto de hora").
The bare form dropped "cuarto" and collapsed to the whole year, because without
the article there was no licensing frame -- now FIXED: the ordinal reading is
also licensed directly before the quarter noun "trimestre".  The clock/room
readings of bare "cuarto" stay untouched (test_nl_confusables: "el cuarto de
baño" -> None).

Gold is pure integer arithmetic: quarter N spans months [3N-2 .. 3N]; the
3rd quarter is already unambiguous ("tercer", not a fraction homograph) and is
the control that the bare frame does not over-fire.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_YEARS = [1999, 2008, 2018, 2025, 2031, 2044, 2050]


def _edges(y, n):
    sm = 3 * n - 2
    if sm == 10:
        return (y, 10), (y + 1, 1)
    return (y, sm), (y, sm + 3)


def _cases():
    out = []
    for ow, n in [("tercer", 3), ("cuarto", 4)]:
        for y in _YEARS:
            (sy, sm), (ey, em) = _edges(y, n)
            out.append((f"{ow} trimestre de {y}", sy, sm, ey, em))
    return out


@pytest.mark.parametrize("text,sy,sm,ey,em", _cases())
def test_bare_worded_quarter_with_year(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1), f"{text!r} start {s}"
    assert e == AstroDate(ey, em, 1), f"{text!r} end {e}"
