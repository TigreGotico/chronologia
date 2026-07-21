"""Czech ranges: "od A do B" (from A to B) and "mezi A a B" (between A and B).

The framing words are the Czech connectors od/do/mezi/a -- ranges are not
English-only.  The span runs from the start of the left endpoint to the end
of the right one.  Between-ranges take instrumental month forms ("mezi
červnem a zářím").
"""
import pytest

from ._corpus import AstroDate, start_end


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,s,e", [
    ("od června do srpna", "2017-6-1", "2017-9-1"),
    ("od ledna do března", "2017-1-1", "2017-4-1"),
    ("od října do prosince", "2017-10-1", "2018-1-1"),
    ("od března do května", "2017-3-1", "2017-6-1"),
    ("od června 2020 do srpna 2021", "2020-6-1", "2021-9-1"),
    ("od ledna 2000 do prosince 2009", "2000-1-1", "2010-1-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("mezi červnem a zářím", "2017-6-1", "2017-10-1"),
    ("mezi dubnem a červnem", "2017-4-1", "2017-7-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


def test_date_range():
    ss, ee = start_end("od 5. června do 12. června")
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)
